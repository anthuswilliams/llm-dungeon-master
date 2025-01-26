import poppler

from pyzerox import zerox
import os
import json
import asyncio

from utils.elastic import elastic_request
import requests


def import_book(book_path):
    # local filepath and file URL supported
    file_path = book_path

    output_dir = "./output_test"  # directory to save the consolidated markdown file
    result = asyncio.run(zerox(file_path=file_path, model="gpt-4o-mini", output_dir=output_dir,
                               select_pages=None))

    print("Importing book is complete")
    return result


def with_subheadings(result):
    import re

    # Initialize the array to store the results
    final_results = []

    # Regular expression to match headings and subheadings
    # Matches markdown headings like # Heading or ## Subheading
    heading_regex = r'^(#+)\s+(.*)'

    # Temporary variables to store current heading, subheading, and content
    current_heading = None
    current_subheading = None
    current_content = []
    current_pages = []

    # Iterate over the pages in the results
    for page_number, page in enumerate(result.pages, start=1):
        lines = page.content.splitlines()
        for line in lines:
            match = re.match(heading_regex, line)
            if match:
                # If a new heading or subheading is found, save the previous one
                if current_heading or current_subheading:
                    final_results.append({"heading": current_heading,
                                          "subheading": current_subheading,
                                          "page": current_pages,
                                          "content": '\n'.join(current_content)})

                # Update the current heading/subheading
                level, title = match.groups()
                if len(level) == 1:
                    # It's a main heading
                    current_heading = title
                    current_subheading = None  # Reset subheading
                elif len(level) > 1:
                    # It's a subheading
                    current_subheading = title

                # Reset content and pages
                current_content = []
                current_pages = [page_number]
            else:
                # Add line to current content
                current_content.append(line)
                if page_number not in current_pages:
                    current_pages.append(page_number)

    # Add the last heading/subheading to the results if needed
    if current_heading or current_subheading:
        key = f"{current_heading or ''}-{current_subheading or ''}-pages:{
            ','.join(map(str, current_pages))}"
        final_results.append({key: '\n'.join(current_content)})

    # Output final results
    return final_results


def without_subheadings(result):
    import re

    # Initialize the array to store the results
    final_results = []

    # Regular expression to match headings and subheadings
    heading_regex = r'^(#)\s+(.*)'  # Matches markdown headings1 like # Heading

    # Temporary variables to store current heading, subheading, and content
    current_heading = None
    current_content = []
    current_pages = []

    # Iterate over the pages in the results
    for page_number, page in enumerate(result.pages, start=1):
        lines = page.content.splitlines()
        for line in lines:
            match = re.match(heading_regex, line)
            if match:
                # If a new heading or subheading is found, save the previous one
                if current_heading:
                    final_results.append({"heading": current_heading,
                                          "page": current_pages,
                                          "content": '\n'.join(current_content)})

                # Update the current heading/subheading
                _, title = match.groups()
                current_heading = title

                # Reset content and pages
                current_content = []
                current_pages = [page_number]
            else:
                # Add line to current content
                current_content.append(line)
                if page_number not in current_pages:
                    current_pages.append(page_number)

    # Add the last heading/subheading to the results if needed
    if current_heading:
        key = f"{
            current_heading or ''}-pages:{','.join(map(str, current_pages))}"
        final_results.append({key: '\n'.join(current_content)})

    # Output final results
    return final_results


def ingest(doc, title, index):
    cleaned_title = title.replace("?", "").replace("/", "-")
    rslt = elastic_request(method=requests.put,
                           url=f"{
                               index}/_doc/{cleaned_title}?pipeline=clean_and_embed",
                           data={"content": doc["content"], "pages": doc["page"]})
    return rslt


def process_ingest(filepath, book_title):
    result = import_book(filepath)
    i = 0
    for rslt in without_subheadings(result):
        if not rslt.get("content"):
            continue
        title = rslt["heading"]
        resp = ingest(rslt, title, book_title)

        try:
            resp.raise_for_status()
        except Exception as e:
            print("Error: ", e)
            print(resp.json())
            raise
        i += 1
        if i % 10 == 0:
            print(rslt)


if __name__ == "__main__":
    process_ingest("/data/Dragonbane/dtrpg-2025-01-13_10-05pm/DB_Path_of_Glory_v1.pdf",
                   "dragonbane--path-of-glory",)
