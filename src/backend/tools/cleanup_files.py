from src.app.worker import cleanup_old_files


def main() -> None:
    cleanup_old_files.send()
    print("cleanup task queued")


if __name__ == "__main__":
    main()
