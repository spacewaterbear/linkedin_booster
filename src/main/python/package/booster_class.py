from datetime import datetime, timezone
import pandas as pd
import numpy as np
from selenium import webdriver
from airtable import Airtable
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random
from package.creds import airtable_creds, linkedin_creds
LOGS_PATH = "logs.txt"

airtable = Airtable(airtable_creds['compte'], airtable_creds['table'], api_key=airtable_creds['api_key'])

class LinkedinBooster:
    def __init__(self, driver, linkedin_d):
        self.driver = driver
        self.website = "https://www.linkedin.com/"
        self.connected = False
        self.linkedin_d = linkedin_d

    def _delay(self, mean=2, sigma=0.2):
        """
        retourn un chiffre aléatoire suivant une distribution normal de moyenne 4 secondes et d'ecart-type de 0.8
        Ce chiffre aléatoire est le délai après chaque clique. Le but est de simuler le comportement d'un humain :
        un délai fixe peut attirer l'attention des contrôleurs, tout comme un délai aléatoire d'une distribution uniforme
        """
        mini = mean*(1-sigma)
        delai = np.random.normal(mean, sigma, 1)[0]
        while delai < mini:
            delai = abs(np.random.normal(mean, sigma, 1)[0])

        sleep(delai)

    def _display_error_message(self, colonne):
        """
        can only been used after the method get_data
        """
        message = f'Problème : {colonne}\n'
        print(message)
        with open(LOGS_PATH, "a+") as f:
            f.write(message)

    def _click_and_delai_xpath(self,xpath, mean=0.6, sigma=0.1):
        try:
            self.driver.find_element_by_xpath(xpath).click()
            self._delay(mean, sigma)
        except :
            self._display_error_message()

    def _from_cn(self, class_name):
        ele_sel = self.driver.find_element_by_class_name(class_name)
        if ele_sel != None:
            return ele_sel.text
        else:
            return None

    def _is_ld_profile(sel, url):
        if r".com/in/" in url:
            return True
        else:
            return False

    def write_message(self, message):
        text_area = self.driver.find_element_by_xpath('//textarea[@name="message"]')
        for letter in message:
            sleep(abs(random.random() / 150))  # sleep between 1 and 3 seconds
            text_area.send_keys(letter)

    def _update_dic(self, column):
        """
        met à jour un dictionnaire qui est créé et remis à zero pour chaque fiche entreprise (cf boucle while plus bas)
        dic : dictionnaire, soit d_xpath ou d_class
        column : nom de la colonne de la dataframe et de la clé du dictionnaire
        """
        try:
            data = self.driver.find_element_by_xpath(self.linkedin_d[column]).text
            if column == "country":
                data = data.split()[-1]
            return data
        except:
            self._display_error_message(column)

    def get_data(self):
        action = True
        if action:
            d = {}
            for key, value in self.linkedin_d.items():
                d[key] = self._update_dic(key)
            d["linkedin_link"] = self.driver.current_url
            d['contacted_in'] = datetime.now(timezone.utc).astimezone().isoformat()
            print(d)
            return d


    ### function for entreprises


    def get_connectable_and_picture_profile_list(self, whole_list, with_profile_pic = True):
        def connectable_and_picture(profile):
            try:
                profile.find_element_by_tag_name("footer")
                if with_profile_pic:
                    image_s = profile.find_element_by_tag_name("img")
                    if not image_s.get_attribute('src').startswith("data:image"):
                        return True
                    else:
                        return False
                else:
                    return True
            except:
                return False

        connectable_list = [profile for profile in whole_list if connectable_and_picture(profile)]

        return connectable_list

    def get_specific_profile(self, whole_list, text_lower_case, text_lower_case2):
        return [profile for profile in whole_list if (text_lower_case or text_lower_case2) in profile.text.lower()]

    #### function for message

    def tag_click(self, tag, texte, click=True):
        """:arg
        WTF this function ?
        """
        try:
            if click:
                self.driver.find_element_by_xpath(f'//{tag}[text()="{texte}"]').click()
                self._delay(0.897,0.21)
        except:
            return self.driver.find_element_by_xpath(f'//{tag}[text()="{texte}"]').text

    def can_connect(self, d):
        try:
            self.driver.find_element_by_xpath('//span[text()="En attente"]').text

            print("{} already request sent".format(d["name"]))
            return False
        except:
            self.driver.find_element_by_xpath('//span[text()="Se connecter"]').click()
            return True

    def sent_message(self, message, d):
        # click on "plus"
        self.driver.find_element_by_xpath('/html/body/div[8]/div[3]/div/div/div/div/div[2]/main/div[1]/section/div[2]/div[1]/div[2]/div/div/div/div/button').click()
        self._delay(0.5,0.2)
        con_possible = self.can_connect(d)
        print(con_possible)
        self._delay(0.5,0.2)
        if con_possible:
            self.tag_click("span", "Ajouter une note")
            self.write_message(message)
            airtable.insert(d)
            self._delay(0.2,0.02)

    def generate_message(self,d):
        full_name = d["name"]
        if "Dr." in full_name:
            name = "Dr. " + full_name.split()[-1]  # take the last name of the list, likely the nom
        else:
            name = full_name.split()[0]  # take the prenom
        message_en = f"Bonjour {name},\nI hope the covid crisis doesn't affect you too much. I was wondering if you already used electrosynthesis to produce one of your APIs ? "
        message_fr = f"Bonjour {name},\nNous sommes tous les deux experts dans l'industrie pharmaceutique et je pense qu'il serait intéressant d'échanger à ce sujet, qu'en dites-vous ?"

        if d["country"] == "France":
            return message_fr
        else:
            return message_en

    def scrap_profile_and_send_message(self):
        d = self.get_data()
        if d['name'] == None:
            d = str(d)
            self._display_error_message(f"pas de nom, pas de message pour {d}\n")
        else:
            message = self.generate_message(d)
            self.sent_message(message, d)

    def click_on_selected_profiles(self, short_list):
        for profile in short_list:
            print(profile.text)
            #     driver.switch_to.window(driver.window_handles[0])
            self.driver.execute_script("arguments[0].scrollIntoView();", profile)
            self._delay(0.2, 0.05)
            self.driver.execute_script("window.scrollTo(0, window.scrollY - 150)")
            self._delay(0.2, 0.05)
            link = profile.find_element_by_tag_name('a').get_attribute('href')
            print(link)
            self.driver.execute_script(f'''window.open("{link}","_blank");''')
            self._delay(0.7, 0.15)
        self.driver.switch_to.window(self.driver.window_handles[0])


    def linkedin_connexion(self):
        self._click_and_delai_xpath('//a[@class="nav__button-secondary"]')
        self.driver.find_element_by_xpath('//input[@id="username"]').send_keys(linkedin_creds['mail'])
        self.driver.find_element_by_xpath('//input[@id="password"]').send_keys(linkedin_creds['pwd'])
        self._click_and_delai_xpath('//button[@type="submit"]', 1.5, 0.2)
        self.connected = True

    def make_a_search(self, text):
        ele = self.driver.find_element_by_class_name('search-global-typeahead__input')
        ele.clear()
        ele.send_keys(text)

    def search_personn(self, keyword_list = [], with_profile_pic=True):
        self.tag_click("a", "Personnes")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._delay(0.7, 0.2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._delay(0.7, 0.2)
        profiles_list = self.driver.find_elements_by_class_name('artdeco-card')
        print('nb profiles :', len(profiles_list))
        short_list = self.get_connectable_and_picture_profile_list(profiles_list, with_profile_pic=with_profile_pic)
        print('nb connectable :', len(short_list))
        if keyword_list != []:
            short_list = self.get_specific_profile(short_list, keyword_list[0], keyword_list[1])
        print('nb connectable :', len(short_list))
        self.click_on_selected_profiles(short_list)

    def send_message_to_profiles(self):
        for tab in self.driver.window_handles:
            self.driver.switch_to.window(tab)
            self._delay(mean=0.2, sigma=0.05)
            print(self.driver.current_url)
            if self._is_ld_profile(self.driver.current_url):
                anwser = input('oui/non\n')
                if anwser == "oui":
                    self.scrap_profile_and_send_message()
                else:
                    self.driver.close()

    def run(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.make_a_search("Sensient")
        ele = self.driver.find_element_by_class_name('search-global-typeahead__input')
        ele.send_keys(Keys.DOWN)
        self._delay(0.5, 0.12)
        ele.send_keys(Keys.DOWN)
        self._delay(0.5, 0.12)
        ele.send_keys(Keys.ENTER)
        self._delay(1.5, 0.2)
        self.search_personn()
        self.send_message_to_profiles()