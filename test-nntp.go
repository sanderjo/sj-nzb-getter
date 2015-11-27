package main

import "fmt"
import "net"
import "bufio"

func main() {
	fmt.Println("Hello, 世界")
	fmt.Println("gaat goed")
	conn, err := net.Dial("tcp", "newszilla6.xs4all.nl:119")
	if err != nil {
		// handle error
	}

	status, err := bufio.NewReader(conn).ReadString('\n')
	fmt.Println(status)

	fmt.Fprintf(conn, "HELP\r\n")
	status, err = bufio.NewReader(conn).ReadString("\n.")
	fmt.Println(status)
	// status, err = bufio.NewReader(conn).ReadString('\n')
	// fmt.Println(status)

}



