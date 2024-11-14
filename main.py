from utils import restaurant_list_txt, Crawler, Parser, merge_tsv_to_csv

def main():
    base_url = "https://guide.michelin.com/en/it/restaurants"
    restaurant_list_txt(base_url, "/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/UrlsLinks.txt")
    Crawler("/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/UrlsLinks.txt", "/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/michelin_html_pages:")
    Parser("/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/michelin_html_pages:", "/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/michelin_tsv_files:")
    merge_tsv_to_csv("/Users/roberto/Desktop/ADM-HM3/directory_HM3_ADM/michelin_tsv_files:", "michelin_restaurants.csv")

if __name__ == "__main__":
    main()
