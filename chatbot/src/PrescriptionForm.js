import React, { useState } from "react";
import { jsPDF } from "jspdf";
import './PrescriptionForm.css';

const PrescriptionForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    weight: "",
    diagnosis: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const currentDate = new Date();
    const formattedDate = currentDate
      .toLocaleDateString("en-GB")
      .replace(/\//g, ""); // Format date as ddmmyy (without spaces or hyphens)

    // Generate the file name as patient_name_date.pdf
    const fileName = `${formData.name}_${formattedDate}.pdf`;
    const dt = currentDate.toLocaleDateString("en-GB"); // Output: "24/12/2024" (dd/mm/yyyy format)
    const formattedTime = currentDate.toLocaleTimeString();

    // Generate the PDF
    const doc = new jsPDF();

    // Set font size for date and time
    doc.setFontSize(12); // Optional adjustment for date/time font size

    // Multi-line text for date and time
    doc.text(`Date: ${dt}`, 10, 10); // Move to the very top
    doc.text(`Time: ${formattedTime}`, 10, 20); // Slightly below date

    // Set font size for patient details
    doc.setFontSize(14); // Adjust as needed

    // Multi-line text for patient name
    doc.text(`Patient Name: ${formData.name}`, 10, 40); // Increased Y for spacing

    // Multi-line text for age
    doc.text(`Age: ${formData.age}`, 10, 60); // Adjusted Y for better alignment

    // Multi-line text for weight
    doc.text(`Weight: ${formData.weight}`, 10, 80); // Adjusted Y for spacing

    // Multi-line text for diagnosis
    const diagnosisText = `Diagnosis: ${formData.diagnosis}`;
    const maxWidth = 180;  // You can adjust the max width as needed for your PDF layout
    const diagnosisLines = doc.splitTextToSize(diagnosisText, maxWidth);
    doc.text(diagnosisLines, 10, 100); // Adjust Y position for more space after weight

    // Convert PDF to a blob
    const pdfBlob = doc.output("blob");

    // Prepare the form data to send the file to Flask server
    const formDataToSend = new FormData();
    formDataToSend.append("file", pdfBlob, fileName);  // Use "pdf" as the key

    // Send the PDF to Flask endpoint
    await fetch("http://localhost:8080/pdf", {
      method: "POST",
      body: formDataToSend,
    });

    alert("PDF generated and sent to server.");
  };

  return (
    <div>
      <h2><center>Prescription</center></h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input
            type="text"
            name="name"
            placeholder="Patient Name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Age:</label>
          <input
            type="number"
            name="age"
            placeholder="Age"
            value={formData.age}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Weight:</label>
          <input
            type="text"
            name="weight"
            placeholder="Weight"
            value={formData.weight}
            onChange={handleChange}
            required
          />
        </div>
        <label >Diagnosis:</label>
        <textarea
          name="diagnosis"
          placeholder="Diagnosis"
          value={formData.diagnosis}
          onChange={handleChange}
          required
        />
        <button type="submit">Generate Prescription</button>
      </form>
    </div>
  );
};

export default PrescriptionForm;
