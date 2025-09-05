# AI Donor Acquisition System - Windows Installation Guide

## Prerequisites

1. **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Make sure to check "Add Python to PATH" during installation
   
2. **Visual Studio Code** - Download from [code.visualstudio.com](https://code.visualstudio.com/)

3. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/)

## Quick Setup

### Method 1: Automatic Setup (Recommended)

1. **Download/Clone the project** to your desired folder
2. **Open Command Prompt** as Administrator
3. **Navigate** to the project folder:
   ```cmd
   cd C:\path\to\donor-acquisition-system
   ```
4. **Run the setup script**:
   ```cmd
   setup_windows.bat
   ```
5. **Wait** for the installation to complete

### Method 2: Manual Setup

1. **Open Command Prompt** in the project directory
2. **Create virtual environment**:
   ```cmd
   python -m venv venv
   ```
3. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate.bat
   ```
4. **Install dependencies**:
   ```cmd
   pip install flask flask-cors scikit-learn openai beautifulsoup4 requests sqlalchemy flask-sqlalchemy
   ```

## Configuration

### 1. OpenAI API Key Setup

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 2. VS Code Setup

1. **Open VS Code**
2. **Open the project folder**: File → Open Folder → Select `donor-acquisition-system`
3. **Install Python extension** (if not already installed)
4. **Select Python interpreter**: 
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose `./venv/Scripts/python.exe`

## Running the Application

### Method 1: Using Batch File
```cmd
run_windows.bat
```

### Method 2: Using VS Code
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Start Flask App"

### Method 3: Manual Command
```cmd
venv\Scripts\activate.bat
python src\main.py
```

## Accessing the Application

Once running, open your web browser and go to:
```
http://localhost:5000
```

## VS Code Features

### Debugging
- Press `F5` to start debugging
- Set breakpoints by clicking on line numbers
- Use the debug console for testing

### Available Debug Configurations:
- **Flask App** - Debug the main application
- **Test Crawler** - Debug the web crawler module
- **Test AI Scoring** - Debug the AI scoring engine

### Tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- **Setup Environment** - Run initial setup
- **Start Flask App** - Launch the application
- **Install Dependencies** - Install/update packages
- **Run Tests** - Execute test suite

## Project Structure

```
donor-acquisition-system/
├── .vscode/                    # VS Code configuration
│   ├── settings.json          # Editor settings
│   ├── launch.json            # Debug configurations
│   └── tasks.json             # Build tasks
├── src/                       # Source code
│   ├── main.py               # Flask application entry point
│   ├── routes/               # API routes
│   ├── models/               # Database models
│   ├── static/               # Frontend files
│   ├── intelligent_donor_crawler.py
│   ├── ai_scoring_engine.py
│   └── personalized_outreach.py
├── venv/                     # Virtual environment (created after setup)
├── setup_windows.bat         # Windows setup script
├── run_windows.bat          # Windows run script
├── requirements.txt         # Python dependencies
└── README_WINDOWS.md        # This file
```

## Troubleshooting

### Common Issues

1. **"Python is not recognized"**
   - Reinstall Python and check "Add to PATH"
   - Or manually add Python to your PATH environment variable

2. **"pip is not recognized"**
   - Usually fixed by reinstalling Python with PATH option
   - Or run: `python -m pip` instead of `pip`

3. **Virtual environment activation fails**
   - Make sure you're in the correct directory
   - Try running as Administrator

4. **Port 5000 already in use**
   - Change the port in `src/main.py`:
     ```python
     app.run(host='0.0.0.0', port=5001, debug=True)
     ```

5. **OpenAI API errors**
   - Verify your API key in the `.env` file
   - Check your OpenAI account has sufficient credits

### Getting Help

1. **Check the console output** for error messages
2. **Use VS Code's integrated terminal** for better error visibility
3. **Enable debug mode** by setting `FLASK_DEBUG=1` in your environment

## Development Tips

### VS Code Extensions (Recommended)
- **Python** - Microsoft
- **Python Docstring Generator** - Nils Werner
- **GitLens** - GitKraken
- **Bracket Pair Colorizer** - CoenraadS
- **Material Icon Theme** - Philipp Kief

### Keyboard Shortcuts
- `Ctrl+Shift+P` - Command Palette
- `F5` - Start Debugging
- `Ctrl+F5` - Run Without Debugging
- `Ctrl+Shift+\`` - New Terminal
- `Ctrl+K Ctrl+S` - Keyboard Shortcuts

### Code Formatting
The project is configured to use Black formatter. Format your code with:
- `Shift+Alt+F` - Format entire file
- `Ctrl+K Ctrl+F` - Format selection

## Next Steps

1. **Configure your OpenAI API key**
2. **Test the crawler** with a small dataset
3. **Customize the scoring algorithm** for your specific needs
4. **Set up email integration** for outreach campaigns
5. **Deploy to production** when ready

## Support

For technical support or questions about the AI Donor Acquisition System, please refer to the main documentation or contact the development team.

