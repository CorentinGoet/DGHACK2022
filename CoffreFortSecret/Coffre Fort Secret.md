# Coffre Fort Secret

- Started on: 2022-11-09
- Last Modified: 2022-11-09

---
- CorentinGoet 
- corentin.goetghebeur@ensta-bretagne.org

---
Challenge Info:
- Category: Dev
- Difficulty: Easy
- Score: 50 points

---

## Challenge

Le coffre-fort secret ne semble pas déchiffrer correctement. Corrigez-le pour obtenir des points. Il y a peut-être d'autres problèmes, qui sait !

- [SecretVault.go](SecretVault.go)

## Write-Up

- [Fixed SecretVault.go](fixed_SecretVault.go)

First, I tried compile the program using:

```bash
go build SecretVault.go
```

This led to an error:
```txt
# command-line-arguments
./SecretVault.go:85:45: cannot use '\n' (untyped rune constant 10) as string value in argument to strings.Replace
```

There is a syntax error in the program on line 85.

I changed it from single quotes to double quotes:

```go
	InputString = strings.Replace(InputString, "\n", "", -1)
```

After this change, the program compiled successfully and the encryption works correctly but the decryption does not detect the encrypted message:

```txt
[corentingoet@DESKTOP-CG SecretVault]$ ./SecretVault HelloWorld
The message was successfully encrypted: HQnREnvjSCrU0w==
[corentingoet@DESKTOP-CG SecretVault]$ ./SecretVault HQnREnvjSCrU0w==
The message was successfully encrypted: HT3TLFHaUTLr9Ihn834aqA==
[corentingoet@DESKTOP-CG SecretVault]$ 
```

Then, we can see that the`main` function always calls the `handleNormalString` function, even with the encrypted message.

We can change:

```go
	if IsBase64(InputString) {
		go handleBase64String(InputString)
	}
	handleNormalString(InputString)
```

To: (I have never used Go before so the syntax is quite new to me but it works with this change)

```go
	if IsBase64(InputString) {
		handleBase64String(InputString)
	} else {
		handleNormalString(InputString)
	}
```

The next error in the code is in the `Decode` function:

```go
func Decode(s string) []byte {
	data, err := base64.StdEncoding.DecodeString(s)
	if err == nil {
		panic(err)
	}
	return data
}
```

The error-check has the wrong comparative operator, which causes the program to panic when everything is fine.

We have to change it to:
```go
func Decode(s string) []byte {
	data, err := base64.StdEncoding.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return data
}
```

Finally, in the `Decrypt` method, the deciphered message is written to the *cipherText* variable instead of the *plainText* variable.

We can change the `Decrypt` function from:

```go
func Decrypt(text, MySecret string) (string, error) {
	block, err := aes.NewCipher([]byte(MySecret))
	if err != nil {
		return "", err
	}
	// We first decode the base64 input text
	cipherText := Decode(text)
	cfb := cipher.NewCFBDecrypter(block, bytes)
	plainText := make([]byte, len(cipherText))
	cfb.XORKeyStream(cipherText, plainText)
	return string(plainText), nil
}
```

To :

```go
func Decrypt(text, MySecret string) (string, error) {
	block, err := aes.NewCipher([]byte(MySecret))
	if err != nil {
		return "", err
	}
	// We first decode the base64 input text
	cipherText := Decode(text)
	cfb := cipher.NewCFBDecrypter(block, bytes)
	plainText := make([]byte, len(cipherText))
	cfb.XORKeyStream(plainText, cipherText)   // CHANGED HERE
	return string(plainText), nil
}
```

Now, if we compile and execute the code, we can successfully encrypt and decrypt messages:

```txt
[corentingoet@DESKTOP-CG SecretVault]$ go build SecretVault.go
[corentingoet@DESKTOP-CG SecretVault]$ ./SecretVault HelloWorld
The message was successfully encrypted: HQnREnvjSCrU0w==
[corentingoet@DESKTOP-CG SecretVault]$ ./SecretVault HQnREnvjSCrU0w==
We believe this may be an encrypted message, here is what it would say: HelloWorld
```
