from typing import Any

import pandasai.pandas as pd
from pandasai.responses.response_parser import ResponseParser
import streamlit as st
from io import BytesIO
from PIL import Image
# Assuming the existence of the to_excel and load_sheet_data functions


import json
import os
import streamlit.components.v1 as components
import pygwalker as pyg

def to_excel(df):
    """
    Convert a DataFrame into a BytesIO Excel object to be used by Streamlit for downloading.
    This function assumes 'df' is a pandas DataFrame.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
    output.seek(0)
    return output

class StreamlitResponse(ResponseParser):
    def __init__(self, context):
        super().__init__(context)

    def format_dataframe(self, result: dict) -> pd.DataFrame:
        """
        Format dataframe generate against a user query
        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        
        if not isinstance(result['value'], pd.DataFrame):
        # If not, convert it to DataFrame (assuming it's convertible directly)
            df = pd.DataFrame(result['value'])
        else:
            df = result['value']
        st.dataframe(df)
        df_xlsx = to_excel(df)  # Ensure this function returns a BytesIO object for Excel
        st.download_button(label='📥 Download to excel',
                           data=df_xlsx,
                           file_name='df_test.xlsx')
        pyg_html = pyg.to_html(df)  # Assuming PyGWalker has a to_html method
        # components.html(pyg_html, height=1000, scrolling=True)
        st.components.v1.html(pyg_html, height=1000, scrolling=True)
        return {'type':result['type'],'value':df}

    def format_plot(self, result) -> dict:
        image_path = result["value"]
        image = Image.open(image_path)
        st.image(image)
        # Iterate over each image path in the list
        with open(image_path, "rb") as file:
            st.download_button(label=f"Download Image",
                            data=file,
                            file_name=f"image.png",
                            mime="image/png")
        # Return the original result dict for consistency
        return {'type': result['type'], 'value': image_path}

    def format_other(self, result):
        if result["type"]=='number' or 'string':
            st.write(result["value"])
        return{'type':result['type'],'value':result['value']}
