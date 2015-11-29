package main

// probably read http://guzalexander.com/2013/12/06/golang-channels-tutorial.html to get more info

import (
	"fmt"
	"time"
)

var c = make(chan int, 5)

func main() {

	go worker(1)
	go worker(2)
	go worker(3)

	for i := 0; i < 40; i++ {
		c <- i
		fmt.Println("into queue", i)
	}

	fmt.Println("Channel filled up!")
	for {
		fmt.Println("Elements in channel:", len(c))
		time.Sleep(2 * time.Second)
		if len(c) == 0 {
			break
		}
	}
	fmt.Println("Done!")

}

func worker(id int) {
	for {
		fmt.Println("Worker", id, "found:", <-c)
		time.Sleep(time.Second)
	}
}

