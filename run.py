
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Cambia debug a False en producción
    app.run(debug=True)
