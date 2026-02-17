import marimo

__generated_with = "0.1.0"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import os

    # Load the database
    db_path = "research/publications.csv"
    if os.path.exists(db_path):
        df = pd.read_csv(db_path)
    else:
        cols = ["Category", "Sub-Category", "Entity", "Affiliation", "Key Work", "SD Relevance/Notes", "Initial Priority", "Rating", "Status", "Detailed Notes", "Link", "Markdown_Path"]
        df = pd.DataFrame(columns=cols)
    
    # Ensure missing columns are added if file existed but was old
    for col in ["Link", "Markdown_Path"]:
        if col not in df.columns:
            df[col] = ""

    mo.md("# 📚 Research Database Tracker")
    return db_path, df, mo, pd, os


@app.cell
def __(df, mo):
    mo.md("## Filter and Explore")
    
    category_filter = mo.ui.multiselect(
        options=sorted(df["Category"].unique().tolist()),
        label="Filter by Category"
    )
    
    priority_filter = mo.ui.multiselect(
        options=["Critical", "High", "Medium", "Low"],
        label="Filter by Priority"
    )
    
    search_input = mo.ui.text(label="Search Entity or Key Work")
    
    mo.hstack([category_filter, priority_filter, search_input])
    return category_filter, priority_filter, search_input


@app.cell
def __(category_filter, df, priority_filter, search_input):
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter.value:
        filtered_df = filtered_df[filtered_df["Category"].isin(category_filter.value)]
        
    if priority_filter.value:
        filtered_df = filtered_df[filtered_df["Initial Priority"].isin(priority_filter.value)]
        
    if search_input.value:
        search_term = search_input.value.lower()
        filtered_df = filtered_df[
            filtered_df["Entity"].str.lower().str.contains(search_term, na=False) | 
            filtered_df["Key Work"].str.lower().str.contains(search_term, na=False)
        ]
        
    return filtered_df,


@app.cell
def __(filtered_df, mo):
    mo.md(f"Showing **{len(filtered_df)}** entries.")
    
    table = mo.ui.table(
        filtered_df[["Category", "Entity", "Key Work", "Initial Priority", "Status", "Rating"]],
        selection="single",
        pagination=True,
        label="Research Publications"
    )
    table
    return table,


@app.cell
def __(df, mo, os, table):
    selected_row = table.value
    
    if not selected_row.empty:
        # Get the full row from the original dataframe based on index/Entity
        entity_name = selected_row.iloc[0]['Entity']
        row = df[df['Entity'] == entity_name].iloc[0]
        
        mo.md(f"### Details: {row['Entity']}")
        
        # Display editable fields
        rating = mo.ui.slider(1, 5, step=1, value=int(row['Rating']) if pd.notna(row['Rating']) and row['Rating'] != '' else 3, label="Rating")
        status = mo.ui.dropdown(options=["To Read", "Reading", "Read", "Skipped"], value=row['Status'] if pd.notna(row['Status']) else "To Read", label="Status")
        notes = mo.ui.text_area(value=row['Detailed Notes'] if pd.notna(row['Detailed Notes']) else "", label="My Notes", full_width=True)
        
        link_ui = mo.md(f"🔗 [Open Original Publication]({row['Link']})") if pd.notna(row['Link']) and row['Link'] != "" else mo.md("🔗 *No link available*")

        # Reader Logic
        reader_ui = mo.md("_No local Markdown version available for this paper._")
        if pd.notna(row['Markdown_Path']) and row['Markdown_Path'] != "":
            if os.path.exists(row['Markdown_Path']):
                with open(row['Markdown_Path'], 'r') as f:
                    content = f.read()
                reader_ui = mo.accordion({"📖 Read Publication Content": mo.md(content)})
            else:
                reader_ui = mo.md(f"⚠️ *Local file not found: {row['Markdown_Path']}*")

        mo.vstack([
            mo.md(f"**Affiliation:** {row['Affiliation']}"),
            mo.md(f"**Key Work:** {row['Key Work']}"),
            mo.md(f"**SD Relevance:** {row['SD Relevance/Notes']}"),
            mo.hstack([rating, status, link_ui]),
            notes,
            reader_ui,
            mo.md("---")
        ])
    else:
        mo.md("_Select a row in the table above to view details and add notes._")
    return (
        entity_name,
        link_ui,
        notes,
        rating,
        reader_ui,
        row,
        selected_row,
        status,
    )


if __name__ == "__main__":
    app.run()
