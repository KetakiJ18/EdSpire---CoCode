from text_extraction import zip_file_extraction
from analysis import analyze_past_papers

original_zip_path = r"C:\Users\ketak\OneDrive\Desktop\BugOff_CO-CODE-JAM\CSF_papers.zip"
destination_folder = r"C:\Users\ketak\OneDrive\Desktop\CO-CODE"

zip_file_extraction(original_zip_path, destination_folder)

syllabus_pdf_path = r"C:\Users\ketak\OneDrive\Desktop\BugOff_CO-CODE-JAM\Computer System Fundamentals.pdf"

ranked_topics = analyze_past_papers(destination_folder, syllabus_pdf_path)
print("Ranked Topics Output:", ranked_topics)  # Debugging step

if ranked_topics:
    print("Ranked Topics based on their occurrences in past papers:")
    print(ranked_topics)
    


