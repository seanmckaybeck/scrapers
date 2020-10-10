import requests
from bs4 import BeautifulSoup # Importing Beautiful soup the web scrapping library....

def scrapeInstagram(soup1):
   
    insta_Data = []                   # Creating empty list called insta_Data for saving the scrapped results....

   
    for meta in soup1.find_all(name="meta", attrs={"property": "og:description"}):     
                                                                                      
        
        insta_Data = meta['content'].split()

    
    followers = insta_Data[0]
    following = insta_Data[2]
    posts = insta_Data[4]

  
    print("\nINSTAGRAM USERNAME :   ", insta_User)   # Printing the Instagram Username....
    print("\nNumber of Posts        :   ", posts)    # Printing Instagram Posts....
    print("\nNumber of Followers    :   ", followers) # Printing User's Followers
    print("\nNumber Following   :   ", following)  # Print User's Following


if __name__ == '__main__':                   # This is the main Driver Code.....

    
    insta_User = input("\nENTER INSTAGRAM USERNAME : ")

   
    insta_URL = "https://www.instagram.com/" + insta_User

    
    insta_Page = requests.get(insta_URL)  

    
    soup = BeautifulSoup(insta_Page.text, "html.parser")

    scrapeInstagram(soup)
