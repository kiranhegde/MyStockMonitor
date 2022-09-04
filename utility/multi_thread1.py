import threading
from threading import Thread
import queue

# def start_thread(*args):
#     t=Thread(target=)


def threads_done(threads,timeout=0.1):
    for thread in threads:
        thread.join(timeout)
        # if thread.

def check_thread_exceptions(exception_queue):
    thread_exceptions=[]
    try:
        while True:
            thread_exceptions.append(exception_queue.get(block=False))
    except queue.Empty:
        return thread_exceptions



class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        t=Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
        # t.start()

    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def print_cube(num):
    """
    function to print cube of given num
    """
    val=num * num * num

    # print("Cube: {}".format(val))
    return  val


def print_square(num):
    """
    function to print square of given num
    """
    val = num * num
    # print("Square: {}".format(val))

    return val


if __name__ == "__main__":
    # creating thread
    # t1 = threading.Thread(target=print_square, args=(10,))
    # t2 = threading.Thread(target=print_cube, args=(10,))
    thread=[]

    t1 = ThreadWithReturnValue(target=print_square, args=(10,))
    thread.append(t1)
    t2 = ThreadWithReturnValue(target=print_cube, args=(10,))
    thread.append(t2)

    # Start the processes (i.e. calculate the random number lists)
    for j in thread:
        j.start()

    # Ensure all of the processes have finished
    result=[]
    for j in thread:
        result.append(j.join())

    print(result)
    #
    # my_queue=queue.Queue
    # while not threads_done(thread):
    #     exceptions = check_thread_exceptions(ThreadWithReturnValue(target=print_square, args=(10,)))


    # # starting thread 1
    # t1.start()
    # # starting thread 2
    # t2.start()
    #
    # # wait until thread 1 is completely executed
    # val=t1.join()
    # print(val)
    # # wait until thread 2 is completely executed
    # val=t2.join()
    # print(val)
    # both threads completely executed
    print("Done!")