import streamlit as st
import pandas as pd
import numpy as np

 
header = st.container()
dataset = st.container()




def ind_DE(var, table): 
    st.write(var, table)

    #Find Individual Design Effect
    all_sum_ind_weight = table["Sum Weights"].sum()
    count_all = table["Count"].sum() 
    design_effect = all_sum_ind_weight/count_all 

    st.write("Individual Design Effect:", design_effect)

#function where each selected column is passed through 
#function: calculate individual design effect
#x = all the unique values in selected column 
def indivdual_DE_table(data, options): 
    
    for var in options:
        x_column = data[var].dropna().unique()
        table = pd.DataFrame([], 
                    columns=["Count", "Weighted", "Weight", "Sum Weights"])
        
        for unique_variable in x_column: 
            #Find Counts:
            count = data[var].value_counts()[unique_variable]
            #example: count = data["Total support:"].value_counts()["Adrian Plank, the Democrat"]
        
            #Find Weighted: 
            weighted = data.groupby([var]).weights.sum()[unique_variable]
            #example: data.groupby(["Total support:"]).weights.sum()["Adrian Plank, the Democrat"]

            #Find Weight
            ind_weight = weighted/count

            #Find Sum Weights
            weight_squared = np.float_power(ind_weight, 2)
            sum_ind_weight = count*weight_squared
            
            entry = pd.DataFrame([[count, weighted, ind_weight, sum_ind_weight]], 
                    columns=["Count", "Weighted", "Weight", "Sum Weights"], 
                    index= [unique_variable])

            table = table.append(entry) 
        ind_DE(var, table)

def prepare_data(data): 
    left_most_col = data.columns.get_loc("State")
    var = data.iloc[:,left_most_col:]
    var = var.select_dtypes(exclude=['bool', 'float64', 'int64'])
    df = pd.DataFrame()
    for i in var.columns:
        df[i] = sorted([var[i].dropna().unique()])
    
    df = df.transpose()
    df.columns = ["Variables"]
    return(df)

def overall_design_effect(data):
    #overall design effect 
    data['weights_squared'] = data["weights"].pow(2) #weight^2 
    sum_weights_sq = data["weights_squared"].sum() #sum of the weights^2
    DE = sum_weights_sq/data.shape[0] #sum of the weights^2 divided by N count 
    return(DE)

with header: 
    st.title("Weight Evaluation")
    st.subheader("A quicker way to evaluate individual weights")
    
with dataset:
    st.subheader("Individual Responses Data")
    st.write("Upload the individual responses data here. Either a csv or xlsx file should work (fingers crossed).")
    # Allow only .csv and .xlsx files to be uploaded
    uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx"])

    # Check if file was uploaded
    if uploaded_file:
        # Check MIME type of the uploaded file
        if uploaded_file.type == "text/csv":
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        # Work with the dataframe
        output_df = prepare_data(data) 
        st.write(output_df)
        options = st.multiselect("Select weighted variables", output_df.index)

        st.subheader("Results")
        indivdual_DE_table(data, options)
        DE = overall_design_effect(data)
        st.write('Overall Design Effect:', DE)
