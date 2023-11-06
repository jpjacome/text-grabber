import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The base URL of the website
base_url = "https://primitivismos.com/page/"

# Initialize a web driver
driver = webdriver.Chrome()

# Function to generate a new filename with an incremental number if it already exists
def get_unique_filename(base_filename, extension):
    index = 1
    while True:
        filename = f"{base_filename}_{index}.{extension}"
        if not os.path.exists(filename):
            return filename
        index += 1

# Check if report and extracted text files exist
report_file_name = "report.txt"
if os.path.exists(report_file_name):
    report_file_name = get_unique_filename("report", "txt")

extracted_file_name = "extracted_text.txt"
if os.path.exists(extracted_file_name):
    extracted_file_name = get_unique_filename("extracted_text", "txt")

# Create a report text file
with open(report_file_name, "w", encoding="utf-8") as report_file:
    page_count = 0
    total_entry_count = 0  # Initialize total entry count

    for page_number in range(1, 60):  # Adjust the range for the number of pages to scrape
        page_count += 1

        # Construct the page URL
        page_url = f"{base_url}{page_number}/"

        # Load the page
        driver.get(page_url)

        # Define a function to check if the page loaded correctly
        def is_page_loaded():
            try:
                driver.find_element(By.ID, 'content')
                return True
            except:
                return False

        # Wait for the page to load or retry if it's not loaded correctly
        wait = WebDriverWait(driver, 10)  # Adjust the wait time if necessary
        wait.until(lambda driver: is_page_loaded())  # Use a lambda function to pass the driver

        # Find the 'content' div
        content_div = driver.find_element(By.ID, 'content')

        # Find the 'entry' divs within 'content'
        entry_divs = content_div.find_elements(By.CLASS_NAME, 'entry')

        missing_entries = []

        # Generate a report for the current page
        report_file.write(f"Page {page_number}:\n")
        if is_page_loaded():
            report_file.write("Page loaded correctly.\n")

            # Iterate over the number of entries found on the page
            for entry_number, entry_element in enumerate(entry_divs, start=1):
                entrytitle = entry_element.find_elements(By.CLASS_NAME, 'entrytitle')
                entrybody = entry_element.find_elements(By.CLASS_NAME, 'entrybody')

                if entrytitle and entrybody:
                    report_file.write(f"Found 'entrytitle' and 'entrybody' for Entry {entry_number}.\n")
                else:
                    report_file.write(f"Missing 'entrytitle' or 'entrybody' for Entry {entry_number}.\n")
                    missing_entries.append(entry_number)

                # Create a text file to store extracted content for each entry
                with open(extracted_file_name, "a", encoding="utf-8") as text_file:
                    entrytitle = entry_element.find_element(By.CLASS_NAME, 'entrytitle')
                    entrybody = entry_element.find_element(By.CLASS_NAME, 'entrybody')

                    h2_element = entrytitle.find_element(By.TAG_NAME, 'h2')
                    h2_text = h2_element.text if h2_element.text else ""

                    body_text = entrybody.text

                    # Replace <p>&nbsp;</p> with empty lines
                    body_text = body_text.replace('<p>&nbsp;</p>', '\n')

                    if h2_text:
                        text_file.write("***\n\n" + h2_text + "\n\n" + body_text + "\n\n")
                    else:
                        text_file.write("***\n\n" + body_text + "\n\n")
        else:
            report_file.write("Page did not load correctly.\n")

        # Update total entry count with the entries found on the current page
        total_entry_count += len(entry_divs)

        # Print the list of entries where 'entrytitle' or 'entrybody' are missing
        if missing_entries:
            report_file.write(f"Missing 'entrytitle' or 'entrybody' for Entries: {', '.join(map(str, missing_entries))}\n")

    # Add the total entry count at the bottom of the report
    report_file.write(f"Total Entries Found: {total_entry_count}\n")

# Close the web driver
driver.quit()
