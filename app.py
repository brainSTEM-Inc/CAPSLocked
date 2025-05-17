from flask import Flask, request, jsonify, render_template, redirect
import requests, pandas as pd, io, copy, sys
sys.setrecursionlimit(2000)


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hola')
def hola():
    roomData = {'Room 195': {'Day 1': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Aidan Paul'], 'Day 2': ['Ritviik Ravi', 'Nikhil Kakani', 'Aileen Sharma', 'Aditya Lahiri', 'James Tan', 'Pranav Gaddam', 'Archit Ashok', 'Rachel Zhang', 'Jay Wankhede', 'Chris Ramos']}}
    #roomData = {'Room 195': {'Day 1': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Aidan Paul'], 'Day 2': ['Nikhil Kakani', 'Jay Wankhede', 'Aditya Lahiri', 'James Tan', 'Pranav Gaddam', 'Rachel Zhang', 'Archit Ashok', 'Aileen Sharma', 'Ritviik Ravi', 'Chris Ramos']}, 'Room 198': {'Day 1': ['Alex Shelley', 'Leavy Hu', 'Esme Liao', 'Veera Singh', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen', 'Katherine Saeed', 'Priscilla Kim', 'Snigdha Chelluri'], 'Day 2': ['Elizabeth Issac', 'Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya', 'David Ruan', 'Daniel Ling', 'Ryan Zhao']}, 'Room 199': {'Day 1': ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee', 'Tarini Nagenalli', 'Tanya Bait', 'Andrew Sha', 'Patrick Foley'], 'Day 2': ['sumedh vangara', 'Milo Stammers', 'Lahari Bandaru', 'Elizabeth Ivanova', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Rohun Sarkar', 'Lakshmi Sangireddi', 'Srinidhi Guruvayurappan']}}
    
    #'Eddie Wu', 
    rawdataDict={'Andrew Sha': [['PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Neuroscience', ['Rohun Sarkar'], [], 'Extracting connectivity signatures of Parkinson’s disease using energy-based analysis'], 'Alex Shelley': [['PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['nan'], [], 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], 'Sachet Korada': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['Patrick Le'], ['Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee'], 'Developing a lightweight, robust, open source control system for a differential drive miniature unmanned ground vehicle'], 'Rohun Sarkar': [['PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Data Science', ['Andrew Sha [DENIED]'], [], 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], 'Leavy Hu': [['PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['Snigdha Chelluri'], [], 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], 'Esme Liao': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st'], 'Biology', ['Kelly Chen'], [], 'Progress in the Generation of an In-House 3rd generation Lentiviral System'], 'David Ruan': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['James Tan'], [], ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], 'Tanya Bait': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Astronomy', ['Srinidhi Guruvayruappan'], [], 'Kinematics of the Ionized Outflow in the Northwest of NGC 253'], 'Vincent Ha': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['nan'], [], 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry'], 'Elizabeth Issac': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science, Biology', ['Sanvika Thimmasamudram'], ['Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya'], 'Using Quantitative Image Analysis and Neural Networks to Classify Colorectal Cancer Patches'], 'Veera Singh': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 5, Tuesday, December 19th'], 'Biology', ['Lahari Bandaru'], [], 'Downregulation of GAP-43 and Y5R Through the Crispri System to Reduce Metastasis of Ewing Sarcoma'], 'Elizabeth Ivanova': [['PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Engineering', ['Tarini Nagenalli or Sumedh Vangara or Tanya Bait [DENIED]'], ['Jeffery Westlake', 'Sanvika Thimmasamudram'], 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], 'Lahari Bandaru': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 5, Tuesday, December 19th'], 'Computer Science, Agriculture', ['Veera Singh'], [], 'DeepQC: A Deep Learning System for Automatic Quality Control of In-situ Soil Moisture Sensor  Time Series Data '], 'Michael Tsegaye': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st'], 'Biology', ['nan'], [], 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], 'Catherine Tenny': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['Aileen Sharma'], [], 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], 'Kelly Chen': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['Esme Liao'], [], 'Characterization of Novel Bispecific Antibodies Against SARS-CoV-2 by Evaluation of Binding Kinetics and Neutralization Assays'], 'Ryan Zhao': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st'], 'Computer Science', ['Zory Teselko'], [], 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], 'Daniel Mathew': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Biology', ['nan'], ['Elizabeth Issac', 'Devon Chen', 'Neel Bhattacharyya'], 'MiniMesh: Real-Time 5,000-Node Anatomical Human Body Mesh Reconstruction for Portable Devices'], 'Akhil Raman': [['PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['Pranav Gaddam'], [], 'WRF HDF5 Reader Integration into Paraview'], 'Hannah Chen': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['Lakshmi Sangireddi [DENIED]'], [], 'Assessing the effect of BomS2 knockdown in drosophila melanogaster glial cells on immune response'], 'Sean Radimer': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['nan'], [], 'How CTF Skill Level Reception to Guidance Influences Performance'], 'Avyukth Selvadurai': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['Daniel Ling'], ['Sachet Korada', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee'], 'The Effect of Cross Laminated Timber on Fire Dynamics'], 'Larson Ozbun': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['nan'], ['Sachet Korada', 'Avyukth Selvadurai', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee'], 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology'], 'Sarah Yu': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['Rachel Zhang'], [], 'Dead Reckoning with TinyML'], 'Milo Stammers': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Math', ['Sumedh Vangara'], [], 'Elementary Generation of SL2 Over Integer Rings of Imaginary Function Fields'], 'sumedh vangara': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Physics', ['milo stammers'], [], 'Electron transport through a 1D chain of dopant-based quantum dots'], 'Tarini Nagenalli': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st'], 'Material Science', ['Priscilla Kim (DENIED]'], [], 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], 'Aaron Zhu': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['nan'], [], 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], 'Eddie Wu': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['Muhammad Ahmad'], [], 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], 'Srinidhi Guruvayurappan': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st'], 'Earth science/Geology', ['Tanya Bait'], [], 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], 'Katherine Saeed': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['nan'], [], 'Comparative Analysis of Short-Read, Long-Read, and Hybrid Bacterial Genome Assembly Across Differen Sequencing Platforms'], 'Lakshmi Sangireddi': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Soil Studies', ['Hannah Chen [DENIED]'], [], 'Investigating Field Capacity Dynamics for Precision Irrigation Management: A Case Study in Agricultural Settings'], 'Patrick Foley': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'nan', ['Aditya Lahiri'], [], 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], 'Nicholas McGonigle': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['nan'], [], 'GPT-Verilog: Enhancing Verilog Generation Using Large Language Models'], 'Zory Teselko': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st'], 'Computer Science', ['Ryan Zhao'], [], 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], 'Muhammad Ahmad': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['Eddie Wu'], ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Patrick Le', 'Ethan Nee'], 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], 'Devon Chen': [['PD 4, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Biology', ['Daniel Ling'], ['Elizabeth Issac', 'Daniel Mathew', 'Neel Bhattacharyya'], 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors'], 'Aidan Paul': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['Aaron Zhu'], [], 'Music Generation using Artificial Neural Networks'], 'Priscilla Kim': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Biology', ['Hannah Chen'], [], 'Finding the underlying mechanism behind PDE11A4 formation '], 'Patrick Le': [['PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['Sachet Korada'], ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Ethan Nee'], 'Mechanical Design of a 3D-Printable Miniature Robotics Platform'], 'Chris Ramos': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st'], 'Computer Science', ['Catherine Tenny'], [], 'Analyzing the Effects of Resampling Techniques on Multiclass Imbalanced Datasets using t-SNE visualizations'], 'Jay Wankhede': [['PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['Neel Bhattacharyya'], [], 'Developing a Large Language Model Powered Algorithm for Enhanced Research Paper Summarization'], 'Nikhil Kakani': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['Ritviik Ravi'], [], 'Optimizing IP Geolocation Algorithm Accuracies: An Integrated Approach Using MLP Neural Network and Reverse DNS Querying Technique'], 'Ritviik Ravi': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th'], 'Computer Science', ['Nikhil Kakani'], [], 'Predicting the Stock Value of NFL Athletes: An Advanced Model Using Gradient-Boosted Trees'], 'Neel Bhattacharyya': [['PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Biology', ['Jay Wankhede'], ['Elizabeth Issac', 'Daniel Mathew', 'Devon Chen'], 'Identifying Predictors of Non-Home Discharge Dispositions Using Artificial Intelligence Among Critically Ill Patients Undergoing Coronary Artery Bypass Grafting'], 'Aileen Sharma': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['Catherine Tenny'], [], 'Aligning Classroom Recording Transcripts with Common Core State Standards using Keyword Extraction'], 'Aditya Lahiri': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['Patrick Foley'], [], 'A Preliminary Method for Identifying Ice Movement in the Arctic'], 'James Tan': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['David Ruan'], [], 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], 'Jeffery Westlake': [['PD 4, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 4, Thursday, December 21st'], 'Computer Science, Engineering', ['nan'], ['Elizabeth Ivanova', 'Sanvika Thimmasamudram'], 'Laser Rangefinding in Explosive Testing'], 'Sanvika Thimmasamudram': [['PD 4, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science, Engineering', ['Elizabeth Isaac'], ['Elizabeth Ivanova', 'Jeffery Westlake'], 'Using MATLAB to Test Camera Sensitivity and for Motion Tracking to Identify Inaccuracies in the Camera used to Record a Building Collapse'], 'Ethan Nee': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Engineering', ['nan'], ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le'], 'Spatial assessments of desalination of groundwater for almond irrigation in California'], 'Pranav Gaddam': [['PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th', 'PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Computer Science', ['nan'], [], 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks'], 'Snigdha Chelluri': [['PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['Leavy Hu'], [], 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells'], 'Rachel Zhang': [['PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['Sarah Yu'], [], 'Automatic Color Flatting of Illustration Linearts'], 'Daniel Ling': [['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st'], 'Biology', ['Devon Chen'], [], 'Unveiling the Role of AND-1 in Tumorigenesis'], 'Archit Ashok': [['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Computer Science', ['nan'], [], 'Using the Kalman Filter to Project the Motion of Ground-Based Obstacles to Prevent Collisions during Autonomous Drone Landings']}
    roomToTimes={'Room 195': {'Day 1': ['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Day 2': ['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st']}, 'Room 198': {'Day 1': ['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Day 2': ['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st']}, 'Room 199': {'Day 1': ['PD 2 Tuesday, December 19th', 'PD 3, Tuesday, December 19th', 'PD 4, Tuesday, December 19th', 'PD 5, Tuesday, December 19th', 'PD 6, Tuesday, December 19th'], 'Day 2': ['PD 2, Thursday, December 21st', 'PD 3, Thursday, December 21st', 'PD 4, Thursday, December 21st', 'PD 5, Thursday, December 21st', 'PD 6, Thursday, December 21st']}}
    personsPerTime=2
    
    
    unboxedRoomData={}
    for room, days in roomData.items():
        thisRoom=[]
        for students in list(days.values()):
            thisRoom.extend(students)
        unboxedRoomData[room]=thisRoom
    
    print(unboxedRoomData)
    
    #unboxedRoomData={'Room 195': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Jay Wankhede', 'Ritviik Ravi', 'Nikhil Kakani', 'Aileen Sharma', 'Archit Ashok', 'Rachel Zhang', 'Pranav Gaddam', 'James Tan', 'Aditya Lahiri', 'Chris Ramos', 'Aidan Paul'], 'Room 198': ['Alex Shelley', 'Leavy Hu', 'Esme Liao', 'Veera Singh', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen', 'Katherine Saeed', 'Priscilla Kim', 'Snigdha Chelluri', 'Daniel Ling', 'Ryan Zhao', 'Elizabeth Issac', 'Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya', 'David Ruan'], 'Room 199': ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee', 'Tarini Nagenalli', 'Tanya Bait', 'Andrew Sha', 'Patrick Foley', 'sumedh vangara', 'Milo Stammers', 'Lakshmi Sangireddi', 'Srinidhi Guruvayurappan', 'Rohun Sarkar', 'Elizabeth Ivanova', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Lahari Bandaru']}
    {'Room 195': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Aidan Paul', 'Chris Ramos', 'Nikhil Kakani', 'Pranav Gaddam', 'Ritviik Ravi', 'Aileen Sharma', 'James Tan', 'Archit Ashok', 'Rachel Zhang', 'Aditya Lahiri', 'Jay Wankhede'], 'Room 198': ['Alex Shelley', 'Leavy Hu', 'Esme Liao', 'Veera Singh', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen', 'Katherine Saeed', 'Priscilla Kim', 'Snigdha Chelluri', 'Daniel Ling', 'Andrew Sha', 'Elizabeth Issac', 'Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya', 'Ryan Zhao', 'David Ruan'], 'Room 199': ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee', 'Milo Stammers', 'Patrick Foley', 'sumedh vangara', 'Tanya Bait', 'Srinidhi Guruvayurappan', 'Rohun Sarkar', 'Elizabeth Ivanova', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Lahari Bandaru', 'Tarini Nagenalli', 'Lakshmi Sangireddi']}
    
    for thisRoom, thisStudents in unboxedRoomData.items():
    
        thisDayTimesFull = roomToTimes[thisRoom]
        thisDayTimes = {key:len(value)*personsPerTime for key,value in roomToTimes[thisRoom].items()}
        thisDays = list(roomToTimes[thisRoom].keys())
        roomSchedule = {key:[] for key in thisDays}
        print(thisDayTimes)
        
        #compromised = []
        
        
        studentAvailability = {}
        for student in thisStudents:
            studentTimes = rawdataDict[student][0]
            availableDays = []
            for day, times in thisDayTimesFull.items():
                if len(set(studentTimes) & set(times)) != 0:
                    availableDays.append(day)
            studentAvailability[student]=availableDays
        
        studentAvailability = dict(sorted(studentAvailability.items(), key=lambda item: len(item[1])))
        #print(studentAvailability)
        
        for student, days in studentAvailability.items():
            
            globalDays = [day for day, number in thisDayTimes.items() if number>0]
            
            '''print(thisDayTimes)
            print(roomSchedule)
            print(globalDays)'''
            
            availableDays = list(set(globalDays) & set(days))
            if len(availableDays)==0:
                #compromised.append(student)
                print(student)
                #availableDays=globalDays
                break
            if len(availableDays)==1:
                roomSchedule[availableDays[0]].append(student)
                thisDayTimes[availableDays[0]]-=1
                continue
            friendDays=[]
            for day in availableDays:
                if len(set(roomSchedule[day]) & set(rawdataDict[student][2]))>0:
                    friendDays.append(day)
            if not friendDays:
                day=sorted(availableDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
            else:
                day=sorted(friendDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
                
            roomSchedule[day].append(student)
            thisDayTimes[day]-=1     
    
        #print(roomSchedule)
        roomData[thisRoom]=roomSchedule
        
    def g(current, students, score, maintopic, day):
        global dataDict
        if not students:
            schedules.append([current,score])
            return
        #try:
        
        for time in list(set(dataDict[students[0]][0]) & set(roomToTimes[maintopic][day])):
            #print(current)
            if len(current[time]) < personsPerTime:
                newSchedule = copy.deepcopy(current)
                newStudents = copy.deepcopy(students)
                newScore=score
                newScore+=len(set(newSchedule[time]) & set(dataDict[students[0]][2]))
                if dataDict[students[0]][3]:
                    newScore+=5*len(set(newSchedule[time]) & set(dataDict[students[0]][3]))
                newSchedule[time].append(students[0])
                newStudents.remove(students[0])
                g(newSchedule, newStudents,newScore, maintopic, day)
                
    
    def f(room, maintopic, day):
        global schedules
        global dataDict
        schedules=[]
        dataDict ={}
        
        for key, value in rawdataDict.items():
            if key in room:
                dataDict[key] = value
    
        realFlexibility = sorted(dataDict, key=lambda x: len(dataDict[x][0]))
        
        currentSchedule = {}
        for time in roomToTimes[maintopic][day]:
            currentSchedule[time]=[]
            
        schedules=[]
        g(currentSchedule, realFlexibility,0, maintopic, day)
        if not schedules:
            return False
        sorted_schedules = sorted(schedules, key=lambda x: x[1], reverse=True)
        print("Schedule w/ nemesi")
        for x in sorted_schedules[:10]:
            print(x)
        print()
        return True
    
    allSchedules={}
    
    #for maintopic, dayTimes in roomData.items():
    maintopic=list(roomData.keys())[0]
    dayTimes=roomData[list(roomData.keys())[0]]
    allSchedules[maintopic]={}
    day=list(dayTimes.keys())[0]
    allSchedules[maintopic][day]=[]
    room = roomData[maintopic][day]
    #print(room)
    schedules=[]
    dataDict ={}

    print(maintopic)
    print(day)
    print(room)
    print()


    firstTry = f(room,maintopic,day)
    if firstTry:
        pass
        allSchedules[maintopic][day].append(["",firstTry])
    else:
        x=True
        for sacrifice in room:
            newRoom = copy.deepcopy(room)
            newRoom.remove(sacrifice)
            secondTry = f(newRoom,maintopic,day)
            if secondTry:
               allSchedules[maintopic][day].append([sacrifice,secondTry])
               print("Sacrifice: "+sacrifice)
               x=False

        if x:
            print("yeah so it sucks")

    print()
    print()

    
    return render_template('hola.html')

realInitRoomDistribution={}
capacityDict={}
rawdataDict={}
personsPerTime=2
roomToTimes={}
dayCapacityDict={}

@app.route('/submit_availability', methods=['POST'])
def submit_availability():

    global realInitRoomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    
    print("🔔 submit_availability was called!")
    data = request.get_json()

    url = data.get('url')
    firstNameCol1 = data.get('firstNameCol')
    lastNameCol1 = data.get('lastNameCol')
    projectNameCol1 = data.get('projectNameCol')
    projectTopicCol1 = data.get('projectTopicCol')
    availabilityCol1 = data.get('availabilityCol')
    friendsCol1 = data.get('friendsCol')
    blurbCol1 = data.get('blurbCol')

    urlData = requests.get(url).content
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    firstNameCol = int(firstNameCol1)-1
    lastNameCol = int(lastNameCol1)-1
    availabilityCol = int(availabilityCol1)-1
    topicCol = int(projectTopicCol1)-1
    friendsCol = int(friendsCol1)-1
    blurbCol= int(blurbCol1)-1
    projectNameCol = int(projectNameCol1)-1
    
    personsPerTime=2
    
    rawdataDict = {}
    #allTimes = ["PD 2 Tuesday, December 19th", "PD 3, Tuesday, December 19th", "PD 4, Tuesday, December 19th", "PD 5, Tuesday, December 19th", "PD 6, Tuesday, December 19th", "PD 2, Thursday, December 21st", "PD 3, Thursday, December 21st", "PD 4, Thursday, December 21st", "PD 5, Thursday, December 21st", "PD 6, Thursday, December 21st"]
    #roomToTimes={element:allTimes for element in ["Room 195","Room 198","Room 199"]}
    
    #roomToTimes = {"Room 195":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 198":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 199":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]}}
    allTimes = data.get('allTimes')
    roomToTimes = data.get('roomsToTimes')
    #print(allTimes)
    #print(roomToTimes)
    
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    capacityDict={"Multiple Topics":0}
    dayCapacityDict={"Multiple Topics": {"Day 1":0}}
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime
        
    for i in range(len(rawData)):
        x = [str(item) for item in rawData.iloc[i]]
        target_string = x[availabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        rawdataDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol]]
    
    
    maintopics = {element for value in rawdataDict.values() for element in value[1].split(", ")}
    rawMaintopics = {value[1] for value in rawdataDict.values()}
    roomData = {}
    for maintopic in maintopics:
        roomData[maintopic]=[]
    
    
    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"
    
    backupRoomDict={}
    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
        if topic not in maintopics:
            backupRoomDict[topic]=[]
    
    for key, value in rawdataDict.items():
        if "," not in value[1]:
            roomData[value[1]].append(key)
        else:
            backupRoomDict[value[1]].append([key,value[4]])
        rawRoomData[value[1]].append(key)
    
    roomData = dict(sorted(roomData.items(), key=lambda item: len(item[1]),reverse=True))
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    initRoomDistribution = {room: [] for room in list(roomToTimes.keys())}
    capacityDictCopy = copy.deepcopy(capacityDict)
    
    for maintopic in list(roomData.keys()):
        #print(capacityDictCopy)
        capacityDictCopy = dict(sorted(capacityDictCopy.items(), key=lambda item: item[1],reverse=True))
        initRoomDistribution[list(capacityDictCopy.keys())[0]].append([maintopic, [[name,rawdataDict[name][4]] for name in roomData[maintopic]]])
        capacityDictCopy[list(capacityDictCopy.keys())[0]]-=len(roomData[maintopic])
    
    
    
    specialGroups=[]
    
    for value in rawRoomData.values():
        if len(value)<=6 and len(value)>1:
            specialGroups.append(value)
    
    for specialGroup in specialGroups:
        for student1 in specialGroup:
                for student2 in specialGroup:
                    if student1 != student2:
                        rawdataDict[student1][3].append(student2)
    
    backupRoomList = []
    for key, value in backupRoomDict.items():
        backupRoomList.append([key,value])
    
    #print(initRoomDistribution)
    #print(rawRoomData)
    #print(backupRoomDict)
    
    realInitRoomDistribution={"Multiple Topics":{"Day 1": backupRoomList}}
    for room, days in roomToTimes.items():
        realInitRoomDistribution[room]={"Day 1":initRoomDistribution[room]}
        for day in list(days.keys())[1:]:
            realInitRoomDistribution[room][day]=[];

    print(realInitRoomDistribution)
    print(dayCapacityDict)
    # Send the data to the frontend
    #return render_template(
           # "hola.html"
       # )
    return render_template('hola.html')

@app.route('/get_data')
def get_data():
    return jsonify({
        "realInitRoomDistribution": realInitRoomDistribution,
        "capacityDict": capacityDict,
        "dayCapacityDict": dayCapacityDict
    })

limit=10

@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    roomData = request.get_json()
    del roomData["Multiple Topics"]
    print("Received schedule:", roomData)
    print(rawdataDict)

    unboxedRoomData={}
    for room, days in roomData.items():
        thisRoom=[]
        for students in list(days.values()):
            thisRoom.extend(students)
        unboxedRoomData[room]=thisRoom
    
    print(unboxedRoomData)
    
    for thisRoom, thisStudents in unboxedRoomData.items():
    
        thisDayTimesFull = roomToTimes[thisRoom]
        thisDayTimes = {key:len(value)*personsPerTime for key,value in roomToTimes[thisRoom].items()}
        thisDays = list(roomToTimes[thisRoom].keys())
        roomSchedule = {key:[] for key in thisDays}
        print(thisDayTimes)
        
        #compromised = []
        
        
        studentAvailability = {}
        for student in thisStudents:
            studentTimes = rawdataDict[student][0]
            availableDays = []
            for day, times in thisDayTimesFull.items():
                if len(set(studentTimes) & set(times)) != 0:
                    availableDays.append(day)
            studentAvailability[student]=availableDays
        
        studentAvailability = dict(sorted(studentAvailability.items(), key=lambda item: len(item[1])))
        #print(studentAvailability)
        
        for student, days in studentAvailability.items():
            
            globalDays = [day for day, number in thisDayTimes.items() if number>0]
            
            '''print(thisDayTimes)
            print(roomSchedule)
            print(globalDays)'''
            
            availableDays = list(set(globalDays) & set(days))
            if len(availableDays)==0:
                #compromised.append(student)
                print(student)
                #availableDays=globalDays
                break
            if len(availableDays)==1:
                roomSchedule[availableDays[0]].append(student)
                thisDayTimes[availableDays[0]]-=1
                continue
            friendDays=[]
            for day in availableDays:
                if len(set(roomSchedule[day]) & set(rawdataDict[student][2]))>0:
                    friendDays.append(day)
            if not friendDays:
                day=sorted(availableDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
            else:
                day=sorted(friendDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
                
            roomSchedule[day].append(student)
            thisDayTimes[day]-=1     
    
        #print(roomSchedule)
        roomData[thisRoom]=roomSchedule
        
    def g(current, students, score, maintopic, day):
        global dataDict
        if not students:
            schedules.append([current,score])
            return
        #try:
        
        for time in list(set(dataDict[students[0]][0]) & set(roomToTimes[maintopic][day])):
            #print(current)
            if len(current[time]) < personsPerTime:
                newSchedule = copy.deepcopy(current)
                newStudents = copy.deepcopy(students)
                newScore=score
                newScore+=len(set(newSchedule[time]) & set(dataDict[students[0]][2]))
                if dataDict[students[0]][3]:
                    newScore+=5*len(set(newSchedule[time]) & set(dataDict[students[0]][3]))
                newSchedule[time].append(students[0])
                newStudents.remove(students[0])
                g(newSchedule, newStudents,newScore, maintopic, day)
    
    def f(room, maintopic, day):
        global schedules
        global dataDict
        schedules=[]
        dataDict ={}
        
        for key, value in rawdataDict.items():
            if key in room:
                dataDict[key] = value
                
        realFlexibility = sorted(dataDict, key=lambda x: len(dataDict[x][0]))
        
        currentSchedule = {}
        for time in roomToTimes[maintopic][day]:
            currentSchedule[time]=[]
            
        schedules=[]
        g(currentSchedule, realFlexibility,0, maintopic, day)
        if not schedules:
            return False
        sorted_schedules = sorted(schedules, key=lambda x: x[1], reverse=True)
        print("Schedule w/ nemesi")
        for x in sorted_schedules[:10]:
            print(x)
        print()
        return True
    
    allSchedules={}
    
    #for maintopic, dayTimes in roomData.items():
    maintopic=list(roomData.keys())[0]
    dayTimes=roomData[list(roomData.keys())[0]]
    allSchedules[maintopic]={}
    for day in list(dayTimes.keys()):
        allSchedules[maintopic][day]=[]
        room = roomData[maintopic][day]
        #print(room)
        schedules=[]
        dataDict ={}

        print(maintopic)
        print(day)
        print(room)
        print()


        firstTry = f(room,maintopic,day)
        if firstTry:
            pass
            allSchedules[maintopic][day].append(["",firstTry])
        else:
            x=True
            for sacrifice in room:
                newRoom = copy.deepcopy(room)
                newRoom.remove(sacrifice)
                secondTry = f(newRoom,maintopic,day)
                if secondTry:
                   allSchedules[maintopic][day].append([sacrifice,secondTry])
                   print("Sacrifice: "+sacrifice)
                   x=False

            if x:
                print("yeah so it sucks")

        print()
        print()
                
        
    return jsonify({"status": "success", "message": "Schedule received"})

if __name__ == '__main__':
    app.run(debug=True)
