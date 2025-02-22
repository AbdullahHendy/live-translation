from thread_manager import ThreadManager

def main():
    thread_manager = ThreadManager()
    
    # Start the threads
    thread_manager.start_threads()

    # Run the thread manager
    thread_manager.run()

if __name__ == "__main__":
    main()
