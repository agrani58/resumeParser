from libraries import *
def convert_docx_to_pdf(docx_resume_path):
        
    if docx_resume_path.endswith(".docx"): 
        try:
                # Initialize COM threading model
            pythoncom.CoInitialize()  # COM allows different software components (written in different languages) to communicate with each other.

                # Define paths for DOCX and the output PDF
            uploaded_resume_path = os.path.splitext(docx_resume_path)[0] + ".pdf"  

                # Initialize Word COM object
            word = comtypes.client.CreateObject("Word.Application")
            word.Visible = False  # Run Word in the background

                # Open DOCX and save as PDF
            in_file = word.Documents.Open(docx_resume_path)
            in_file.SaveAs(uploaded_resume_path, FileFormat=17)  # PDF format constant
            in_file.Close()
            word.Quit()

        except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
                return None
        finally:
                # Uninitialize COM after usage
                pythoncom.CoUninitialize()

        return uploaded_resume_path  # Return the path to the converted PDF file
def is_valid_date(date_str):
    """Check if date matches mm/yyyy or Month YYYY format"""
    if not isinstance(date_str, str):
        return False
    # Check for Month YYYY format (e.g., "May 2023")
    if len(date_str.split()) == 2:
        month, year = date_str.split()
        if month.lower() in ["january", "february", "march", "april", "may", "june",
                        "july", "august", "september", "october", "november", "december"]:
            return year.isdigit() and len(year) == 4
        
    # Check for mm/yyyy format (e.g., "05/2023")
    if len(date_str.split('/')) == 2:
        month, year = date_str.split('/')
        return month.isdigit() and 1 <= int(month) <= 12 and year.isdigit() and len(year) == 4
    
    if date_str in ["Present", "N/A"]:
        return True
def _tracker(data, missing, path="", strict=False):
    if isinstance(data, dict):
        has_missing_date = False  # Track if job entry has missing dates
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                _tracker(value, missing, new_path, strict)
            else:
                # Check if the field is an invalid/missing date
                if key.lower() in ["start_date", "end_date"] and not is_valid_date(str(value)):
                    missing.append(new_path)
                    has_missing_date = True  # Mark job entry as having missing dates
                elif str(value).strip().upper() in ["N/A", "NA", "NONE", ""]:
                    missing.append(new_path)
        
        # If dates are missing, check if description should also be flagged
        if has_missing_date and "description" in data and str(data["description"]).strip():
            missing.append(f"{path}.description")

        if not data and path:
            missing.append(path)

    elif isinstance(data, list):
        if not data and path:
            missing.append(path)
        for idx, item in enumerate(data):
            new_path = f"{path}[{idx}]" if path else f"[{idx}]"
            if isinstance(item, (dict, list)):
                _tracker(item, missing, new_path, strict)
            else:
                if str(item).strip().upper() in ["N/A", "NA", "NONE", ""]:
                    missing.append(new_path)
