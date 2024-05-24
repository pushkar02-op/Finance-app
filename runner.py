import webbrowser
import data_entry_db



# Run the commands in separate command prompt windows
if __name__ == '__main__':
    # Run App 1
    data_entry_db.app.run(debug=True, port=5000)


# Open a website in the default web browser
webbrowser.open("http://127.0.0.1:5000/")
webbrowser.open("http://127.0.0.1:5001/")