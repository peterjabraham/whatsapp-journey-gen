# WhatsApp Journey Generator

A web application that generates WhatsApp marketing journey documentation using multiple AI models via OpenRouter API.

## Features

- Upload prompt markdown files
- Select 1-3 AI models from a curated list
- Generate journey documentation (markdown + HTML visualizations)
- Download results as a zip file
- Clean, modern web interface

## Local Development

### Prerequisites

- Python 3.9+
- OpenRouter API key

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   Create a `.env` file in the project root:
   ```
   OPENROUTER_API_KEY=sk-or-your-api-key-here
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the web interface:**
   Open http://localhost:5000 in your browser

### Running Tests

```bash
python -m pytest test_app.py -v
```

## Deployment to Railway

### Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)

### Deployment Steps

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect Railway to GitHub:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variable:**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add new variable:
     - Name: `OPENROUTER_API_KEY`
     - Value: Your OpenRouter API key (starts with `sk-or-`)

4. **Deploy:**
   - Railway will automatically detect Python/Flask
   - It will install dependencies from `requirements.txt`
   - The app will deploy automatically

5. **Get your URL:**
   - Railway provides a public URL (e.g., `your-app.railway.app`)
   - You can set a custom domain in Railway settings

### Railway Configuration

The app uses:
- `Procfile` - Tells Railway to run `gunicorn app:app`
- `requirements.txt` - Python dependencies
- Environment variable `OPENROUTER_API_KEY` - Your API key

## Usage

1. **Upload a prompt file:**
   - Click the file upload area
   - Select your `.md` prompt file (e.g., `PROMPT_4_WhatsApp_Journey_Generator.md`)

2. **Enter scenario:**
   - Type a description of your scenario
   - Example: "Lifetime ISA for UK Police, 25-40, UK, WATI journeys"

3. **Select models:**
   - Choose 1-3 models from the checklist
   - Maximum 3 models allowed per generation

4. **Generate:**
   - Click "Generate Journeys"
   - Wait for processing (may take several minutes)
   - Zip file will automatically download when complete

5. **Extract and view:**
   - Unzip the downloaded file
   - Open HTML files in your browser to view visualizations

## File Structure

```
outputs/
  {scenario_slug}/
    {model_slug}/
      journey.md
      full_detailed.html
      workflow_overview.html
```

## Available Models

Models are configured in `models.json`. To add or modify models, edit this file and redeploy.

Current models:
- x-ai/grok-4.1-fast
- google/gemini-3-pro-preview
- openai/gpt-5.1
- openai/gpt-4.1-mini
- anthropic/claude-3.5-sonnet
- meta-llama/llama-3.1-70b-instruct

## Cost

- **Railway.app**: $5/month (always on, reliable)
- **Free trial**: $5 credit monthly (may cover light usage)
- **OpenRouter API**: Pay per use (varies by model)

## Troubleshooting

### API Key Issues
- Ensure `OPENROUTER_API_KEY` is set in Railway environment variables
- Check that the key starts with `sk-or-`
- Verify the key is active in your OpenRouter dashboard

### File Upload Issues
- Maximum file size: 5MB
- Only `.md` files are accepted
- Ensure the file contains valid markdown

### Generation Errors
- Check that at least 1 model is selected
- Maximum 3 models allowed
- Ensure scenario description is provided
- Check Railway logs for detailed error messages

## License

MIT
