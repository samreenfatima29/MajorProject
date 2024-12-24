import os
import pandas as pd
from fpdf import FPDF

# Load the dataset
file_path = "merged_dataset.csv"  # Replace with your file path
df = pd.read_csv(file_path)

# Ensure directories exist
output_dir = "Patient_Folders"
os.makedirs(output_dir, exist_ok=True)

# Create a class for generating PDFs
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Patient Medical Record', align='C', ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Function to map field descriptions
def map_field_description(record):
    mappings = {
        "height": f"{record['height']} cm",
        "weight": f"{record['weight']} kg",
        "ap_hi": f"{record['ap_hi']} (Systolic blood pressure)",
        "ap_lo": f"{record['ap_lo']} (Diastolic blood pressure)",
        "cholesterol": f"{record['cholesterol']} (1: normal, 2: above normal, 3: well above normal)",
        "gluc": f"{record['gluc']} (1: normal, 2: above normal, 3: well above normal)",
        "smoke": f"{'Yes' if record['smoke'] == 1 else 'No'} (whether patient smokes)",
    }
    return mappings

# Group records by patient_ID
for patient_id, group in df.groupby('patient_ID'):
    # Create a folder for each patient_ID
    patient_folder = os.path.join(output_dir, str(patient_id))
    os.makedirs(patient_folder, exist_ok=True)
    
    # Generate a PDF for each record under this patient_ID
    for idx, record in group.iterrows():
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)

        # Add content to the PDF
        pdf.cell(0, 10, f"Patient ID: {patient_id}", ln=True)
        pdf.cell(0, 10, f"Age: {record['age']} years", ln=True)
        pdf.cell(0, 10, f"Gender: {'Male' if record['gender'] == 1 else 'Female'}", ln=True)
        
        # Map and display field descriptions
        descriptions = map_field_description(record)
        for field, description in descriptions.items():
            pdf.cell(0, 10, f"{field.capitalize()}: {description}", ln=True)
        
        # Save the PDF with 'id' as the name
        pdf_path = os.path.join(patient_folder, f"{int(record['id'])}.pdf")
        pdf.output(pdf_path)
        print(f"Generated PDF: {pdf_path}")

print(f"All PDFs have been generated and saved under '{output_dir}'")