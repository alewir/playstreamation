import info_collector
import info_window


def main():
    ict = info_collector.InfoCollectorThread()
    ict.start()

    frame = info_window.create(ict)
    info_window.show()


if __name__ == "__main__":
    main()

