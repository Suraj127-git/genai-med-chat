from shared.mongo import get_db, init_db


def main():
    db = get_db()
    init_db(db)


if __name__ == "__main__":
    main()
