SERVER=$1

case "$SERVER" in
    "api")
    uvicorn api.app:app --host 0.0.0.0 --port 80
    ;;
    "gradio")
    python -m tuning.gradio_demo
    ;;
    *)
    ;;
esac