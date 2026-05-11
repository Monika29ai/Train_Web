
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset
df = pd.read_csv('Train_Info.csv')

# Convert time columns
for col in ['Arrival_time', 'Departure_Time']:
    df[col] = pd.to_datetime(df[col], format='%H:%M:%S', errors='coerce')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    source = request.form['source']
    destination = request.form['destination']

    results = []

    grouped = df.groupby('Train_No')

    for train_no, train_data in grouped:

        train_data = train_data.reset_index(drop=True)

        source_rows = train_data[train_data['Station_Name'].str.lower() == source.lower()]
        dest_rows = train_data[train_data['Station_Name'].str.lower() == destination.lower()]

        if not source_rows.empty and not dest_rows.empty:

            source_index = source_rows.index[0]
            dest_index = dest_rows.index[0]

            if source_index < dest_index:

                source_departure = source_rows.iloc[0]['Departure_Time']
                dest_arrival = dest_rows.iloc[0]['Arrival_time']

                if pd.notnull(source_departure) and pd.notnull(dest_arrival):

                    duration = dest_arrival - source_departure

                    if duration.total_seconds() < 0:
                        duration += pd.Timedelta(days=1)

                    hours, remainder = divmod(duration.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)

                    duration_text = f"{hours} hrs {minutes} mins"

                else:
                    duration_text = "Not Available"

                results.append({
                    'train_no': train_no,
                    'departure': source_departure.strftime('%H:%M') if pd.notnull(source_departure) else 'N/A',
                    'arrival': dest_arrival.strftime('%H:%M') if pd.notnull(dest_arrival) else 'N/A',
                    'duration': duration_text
                })

    return render_template(
        'results.html',
        results=results,
        source=source,
        destination=destination
    )


if __name__ == '__main__':
    app.run(debug=True)
