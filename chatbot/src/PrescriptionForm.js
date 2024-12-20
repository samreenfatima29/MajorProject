import React, { useState } from "react";
import { jsPDF } from "jspdf";
import './PrescriptionForm.css'
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
  
    // Get the current date and time
    const currentDate = new Date();
    const formattedDate = currentDate
      .toLocaleDateString("en-GB")
      .replace(/\//g, ""); // Format date as ddmmyy (without spaces or hyphens)
  
    // Generate the file name as patient_name_date.pdf
    const fileName = `${formData.name}_${formattedDate}.pdf`;
  
    // Generate the PDF
    const doc = new jsPDF();
  
    // Include patient details and date/time in the PDF
    doc.text(`Patient Name: ${formData.name}`, 10, 10);
    doc.text(`Age: ${formData.age}`, 10, 20);
    doc.text(`Weight: ${formData.weight}`, 10, 30);
    doc.text(`Diagnosis: ${formData.diagnosis}`, 10, 40);
  
    doc.text(`Date: ${formattedDate}`, 10, 50);
  
    // Convert PDF to a blob
    const pdfBlob = doc.output("blob");
  
    // Prepare the form data to send the file to the Flask server
    const formDataToSend = new FormData();
    formDataToSend.append("pdf", pdfBlob, fileName); // Use "pdf" as the key
  
    // Send the PDF to the Flask endpoint
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
