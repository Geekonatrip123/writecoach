# IREL_Hackathon
# WriteCoach - AI-Powered Writing Assistant


WriteCoach is a cloud-native AI writing assistant that helps users improve their writing across different formats using Google Gemini AI. Built with a microservices architecture, it provides real-time analysis, format-specific suggestions, and progress tracking.

## 🌟 Live Demo
https://drive.google.com/file/d/1rGY4-hTlDnY4NBjmBzy2xHkb_zNt_QEl/view?usp=sharing:- You can view the video demo here

- **Application**: https://writecoach-2.onrender.com
- **API Documentation**: https://writecoach-api-zmur.onrender.com/docs

## 🚀 Features

- **AI-Powered Analysis**: Leverages Google Gemini for intelligent writing suggestions
- **Multi-Format Support**: Optimized for emails, reports, essays, and general text
- **Real-Time Feedback**: Instant readability scores and improvement suggestions
- **Progress Tracking**: Visual analytics to monitor writing improvement over time
- **RESTful API**: Well-documented API with Swagger/OpenAPI support
- **Cloud-Native**: Containerized with Docker and deployed on Render

## 🏗️ Architecture

WriteCoach uses a microservices architecture with 6 independent services:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Streamlit UI   │    │     CLI App      │    │   API Docs      │
└────────┬────────┘    └────────┬─────────┘    └────────┬────────┘
         │                      │                        │
         └──────────────────────┼────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   FastAPI Gateway   │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌────────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│ Text Analyzer   │  │ Format Detector  │  │ Suggestion Gen. │
└─────────────────┘  └──────────────────┘  └────────┬────────┘
                                                     │
                               ┌─────────────────────▼────────┐
                               │     Google Gemini AI         │
                               └──────────────────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Streamlit
- **AI/ML**: Google Gemini AI, NLTK
- **Data Visualization**: Plotly
- **Containerization**: Docker
- **Deployment**: Render
- **API Documentation**: Swagger/OpenAPI

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (optional)
- Google Gemini API key

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Geekonatrip123/writecoach.git
cd writecoach
```

2. Install dependencies:
```bash
pip install -r requirements.txt
python -m nltk.downloader punkt averaged_perceptron_tagger punkt_tab
```

3. Set up environment variables:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

4. Run the services:

```bash
# Terminal 1: Start API
python api.py

# Terminal 2: Start Streamlit UI
streamlit run app.py
```

### Docker Deployment

```bash
docker-compose up --build
```

## 🚀 Deployment

The application is deployed on Render with the following services:

1. **API Service**: Handles all backend processing
2. **Streamlit Service**: Provides the user interface

### Environment Variables

```
GOOGLE_API_KEY=your-gemini-api-key
NLTK_DATA=/opt/render/nltk_data
```

## 📚 API Documentation

The API documentation is available at:
- Swagger UI: https://writecoach-api-zmur.onrender.com/docs
- ReDoc: https://writecoach-api-zmur.onrender.com/redoc

### Key Endpoints

- `POST /analyze`: Analyze text and get suggestions
- `GET /health`: Health check endpoint
- `GET /api/v1/progress/{user_id}`: Get user progress data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

- **Shlok** - [GitHub](https://github.com/Geekonatrip123)

## 🙏 Acknowledgments

- Google Gemini AI for powerful language processing
- Streamlit for the intuitive UI framework
- FastAPI for the high-performance API framework

---

Built with ❤️ for IREL Hackathon
