package main

import (
	"fmt"
	"io"
	"net"
	"strings"
"strconv"
)

func getoneline(thisconn net.Conn) string {
	// get one line
	buf := make([]byte, 0, 4096) // full line buffer
	tmp := make([]byte, 1)       // reading tmp buffer
	for {
		n, err := thisconn.Read(tmp)
		if err != nil {
			if err != io.EOF {
				fmt.Println("read error:", err)
			}
			break
		}
		buf = append(buf, tmp[:n]...)
		position := strings.Index(string(buf), "\r\n")
		if position > -1 {
			break
		}
	}
	// fmt.Println("total size:", len(buf))
	return string(buf)
}

func getuntildot(thisconn net.Conn) {
	buf := make([]byte, 0, 4096000) // big buffer
	tmp := make([]byte, 4096)       // reading tmp buffer
	for {
		n, err := thisconn.Read(tmp)
		if err != nil {
			if err != io.EOF {
				fmt.Println("read error:", err)
			}
			break
		}
		buf = append(buf, tmp[:n]...)
		position := strings.Index(string(buf), "\r\n.\r\n")
		if position > -1 {
			break
		}
	}
	// fmt.Println("total size:", len(buf))
	fmt.Println(string(buf))
}

func setupconnection(newsserver string, port int, username string, password string) (net.Conn, error) {
	conn, err := net.Dial("tcp", newsserver + ":" + strconv.Itoa(port))
	if err != nil {
		fmt.Println("dial error:", err)
		return conn, err
	}
	welcome := getoneline(conn)
	fmt.Println("Welcome message is", welcome)

	// Send a BODY command to see if authentication is needed:
	fmt.Fprintf(conn, "BODY <bla@bla>\r\n")
	result := getoneline(conn)
	// fmt.Println("result is", result)
	if strings.Index(result, "480") == 0 {
		fmt.Println("Authentication required")
		// Authentication required
		fmt.Fprintf(conn, "AUTHINFO USER " + username + "\r\n")
		result = getoneline(conn)
		fmt.Println("result is", result)	
		fmt.Fprintf(conn, "AUTHINFO PASS " + password + "\r\n")
		result = getoneline(conn)
		fmt.Println("result is", result)	
	}
	if strings.Index(result, "430") == 0 {
		fmt.Println("No authentication required")
		// No authentication required
	}
	return conn, err
}



func main() {

	//conn, _ := setupconnection("newszilla.xs4all.nl", 119, "testing", "blabla")
	//conn, _ := setupconnection("news.caiway.nl", 119, "blabla@caiway.nl", "blabla")
	conn, _ := setupconnection("newszilla6.xs4all.nl", 119, "", "")


	fmt.Fprintf(conn, "HELP\r\n")
	fmt.Println(getoneline(conn))
	getuntildot(conn)

	fmt.Fprintf(conn, "QUIT\r\n")
	fmt.Println(getoneline(conn))
	conn.Close()
}
