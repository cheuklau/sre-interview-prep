# Lecture 11

## I/O Functions of Standard C Library

- `fopen()`, `fclose()`: open and close a file
- `fgetc()`, `fputc()`: reading/writing one character at a time
- `fgets()`, `fputs()`: reading/writing line by line
- `fscanf()`, `fprintf()`: reading/writing using formatted I/O
- `fseek()`, `ftell()`, `fgetpos()`, `fsetpos()`, `rewind()`: get information or change current file offset of a file

## UNIX More Utility

- `more <file>` opens, displays contents of file then quits
- `more <file1> <file2>` will display contents of each file with spacebar to scroll through files
- `more <longfile>` will display one page of file, and will wait for spacebar to scroll through file
- Note `$LINES` is env var to set number of lines terminal is displaying
- More pauses waiting for a corrector
    * `q` will quit the program
    * `enter` will display one more line and percentage is also updated
    * `spacebar` will display a new page
    * `/<search term>` will find the first occurence of the search term
- `ls /bin | more`
- Many of the tasks to implement `more` requires system calls (can't be done strictly with C library calls)

## How Does more do it?

1. Show `P-1` lines from file passed as cmd line arg where `P` is number of lines terminal can show
2. Show `--More--(54%)` messages after `P-1` lines
3. Wait for commands
4. If command is `'\n'` character, advance one line and go to step 2
5. If command is `' '` character, go to step 1
6. If command is `'q'` character, exit

## Version 0

- Get a single file name via command line, display entire contents of file and exit
- `morev0.c`
```
#include <stdio.h>
#include <stdlib.h>
#define LINELEN 512
void do_more(FILE *);
int main(int argc , char *argv[]){
    // No command line argument
   if (argc == 1){
       printf("This is the help page\n");
       exit (0);
   }
   FILE * fp;
   // Calls fopen library function in read mode assuming the first argument passed in is the path to the file
   // fopen returns a file pointer
   fp = fopen(argv[1] , "r");
   if(fp == NULL){
       perror("Can't open file");
       exit(1);
   }
   // Call function to read contents of file and displays it on screen
   do_more(fp);
   // Close file
   fclose(fp);
   // Program quits
   return 0;
}

void do_more(FILE *fp){
    // Creates buffer of 512 bytes (assumes any line of the file is not longer than 512 bytes)
   char buffer[LINELEN];
   // Uses fgets library function to read the file pointed to by fp and place in the buffer
   // while loop repeats until fgets hit EOF at which point it returns NULL and the loop breaks
   while(fgets(buffer, LINELEN, fp)){
       // Print line to stdout
      fputs(buffer, stdout);
   }
}
```

## Version 1

- This time we handle multiple files
```
#include <stdio.h>
#include <stdlib.h>
#define LINELEN 512
void do_more(FILE *);
int main(int argc , char *argv[]){
   if (argc == 1){
       printf("This is the help page\n");
       exit (0);
   }
   int i = 0;
   FILE * fp;
   // Loop over all arguments
   while(++i < argc){
      fp = fopen(argv[i] , "r");
      if (fp == NULL){
         perror("Can't open file");
         exit (1);
      }
   do_more(fp);
   fclose(fp);
   }
   return 0;
}

void do_more(FILE *fp){
   char buffer[LINELEN];
   while (fgets(buffer, LINELEN, fp)){
      fputs(buffer, stdout);
   }
}
```

## Version 2

- Display one page at a time and pause for commands ('q', ' ', '\n') and act accordingly
```
#include <stdio.h>
#include <stdlib.h>

#define	PAGELEN	20  // Assume screen is fixed at 20 lines
#define	LINELEN	512 // Still assume line length is at most 512 characters

void do_more(FILE *);
int  get_input();
int main(int argc , char *argv[])
{
   int i=0;
   if (argc == 1){
       printf("This is the help page\n");
       exit (0);
   }
   FILE * fp;
   while(++i < argc){
      fp = fopen(argv[i] , "r");
      if (fp == NULL){
         perror("Can't open file");
         exit (1);
      }
      do_more(fp);
      fclose(fp);
   }
   return 0;
}

void do_more(FILE *fp)
{
   int num_of_lines = 0;
   int rv;
   char buffer[LINELEN];
   while (fgets(buffer, LINELEN, fp)){
      fputs(buffer, stdout);
      // Every time we display a line we increment the line counter
      num_of_lines++;
      // Once the lines equal to the page length
      // We call the get input function that is going to get input from the user
      if (num_of_lines == PAGELEN){
         rv = get_input();
         if (rv == 0)//user pressed q
            break;//
         else if (rv == 1)//user pressed space bar
            num_of_lines -= PAGELEN;
         else if (rv == 2)//user pressed return/enter
	    num_of_lines -= 1; //show one more line
         else if (rv == 3) //invalid character
            break;
      }
  }
}

int get_input()
{
   int c;
    // Gets a character from the keyboard
     c=getchar();
      if(c == 'q')
	 return 0;
      if ( c == ' ' )
	 return 1;
      if ( c == '\n' )
	 return 2;
      return 3;
   return 0;
}
```

## A Bit About Terminals

- Terminal is a device used to communicate with a process
- Consists of a keyboard and a visual display unit
- We have used `printf()` function to display text on standard output
- We know that first argument to `printf` is a format string which can contain:
    * Text to be displayed
    * Escape sequence characters
    * Special specifiers
- We can also use Control Sequence Introducer (`\033[`) and after this we can use a specific Terminal Control Code using which we can change how the text is displayed on the screen, can control the movement of the cursor as well as can clear parts of the screen
- Example
```
#include <stdio.h>
#include <unistd.h>

int main(int argc, char* argv[])
{
//how to display text
printf("\e[7m This is in reverse video\n");
printf("\033[m This is in normal video\n");
printf("\033[1m This is bold \033[m \n");
printf("\033[4m This is underlined \033[m \n");

//Changing foreground and background colours
printf("\033[35m \033[40m This is in magenta colour with black back ground \033[39m \033[49m\n");

//cursor movement
printf("\033[10G This will start from column 10 \n");
printf("\033[10;20H This will appear in row 10 column 20 \n");
printf("\033[5B This is going to appear 5 lines below \n");

getchar();
//clearing parts of the screen
printf("\033[2J");
return 0;
}
```

## Version 3

- Add a feature that displays a message in reverse video at the last line `--more--(?%)` without the percentage actually calculated
```
#include <stdio.h>
#include <stdlib.h>

#define	PAGELEN	20
#define	LINELEN	512

void do_more(FILE *);
int  get_input();
int main(int argc , char *argv[])
{
   int i=0;
   if (argc == 1){
       printf("This is the help page\n");
       exit (0);
   }
   FILE * fp;
   while(++i < argc){
      fp = fopen(argv[i] , "r");
      if (fp == NULL){
         perror("Can't open file");
         exit (1);
      }
      do_more(fp);
      fclose(fp);
   }
   return 0;
}

void do_more(FILE *fp)
{
   int num_of_lines = 0;
   int rv;
   char buffer[LINELEN];
   while (fgets(buffer, LINELEN, fp)){
      fputs(buffer, stdout);
      num_of_lines++;
      if (num_of_lines == PAGELEN){
         rv = get_input();
         if (rv == 0){//user pressed q
            // Move one line up, clear current line, take cursor back to first column of same line
            printf("\033[1A \033[2K \033[1G");
            break;
         }
         else if (rv == 1){//user pressed space bar
            printf("\033[1A \033[2K \033[1G");
            num_of_lines -= PAGELEN;
         }
         else if (rv == 2){//user pressed return/enter
            printf("\033[1A \033[2K \033[1G");
	         num_of_lines -= 1; //show one more line
            }
         else if (rv == 3){ //invalid character
            printf("\033[1A \033[2K \033[1G");
            break;
         }
      }
  }
}

int get_input()
{
   int c;
   // Display a message in reverse video (only change to this version)
   printf("\033[7m --more--(%%) \033[m");
     c=getchar();
      if(c == 'q')
	 return 0;
      if ( c == ' ' )
	 return 1;
      if ( c == '\n' )
	 return 2;
      return 3;
   return 0;
}
```

## Version 4

- Handle I/O redirection
```
#include <stdio.h>
#include <stdlib.h>

#define	PAGELEN	20
#define	LINELEN	512

void do_more(FILE *);
int  get_input(FILE*); // Add file open which is going to be /dev/tty
int main(int argc , char *argv[])
{
   int i=0;
   // If no argument from commandline then call do_more with standard input
   // Which will allow us to pipe output of another program into this program
   if (argc == 1){
      do_more(stdin);
   }
   FILE * fp;
   while(++i < argc){
      fp = fopen(argv[i] , "r");
      if (fp == NULL){
         perror("Can't open file");
         exit (1);
      }
      do_more(fp);
      fclose(fp);
   }
   return 0;
}

void do_more(FILE *fp)
{
   int num_of_lines = 0;
   int rv;
   char buffer[LINELEN];
   // Open the terminal as the file pointer
   FILE* fp_tty = fopen("/dev//tty", "r");
   while (fgets(buffer, LINELEN, fp)){
      fputs(buffer, stdout);
      num_of_lines++;
      if (num_of_lines == PAGELEN){
         rv = get_input(fp_tty);
         if (rv == 0){//user pressed q
            printf("\033[1A \033[2K \033[1G");
            break;//
         }
         else if (rv == 1){//user pressed space bar
            printf("\033[1A \033[2K \033[1G");
            num_of_lines -= PAGELEN;
         }
         else if (rv == 2){//user pressed return/enter
            printf("\033[1A \033[2K \033[1G");
	         num_of_lines -= 1; //show one more line
            }
         else if (rv == 3){ //invalid character
            printf("\033[1A \033[2K \033[1G");
            break;
         }
      }
  }
}

int get_input(FILE* cmdstream)
{
   int c;
   printf("\033[7m --more--(%%) \033[m");
     c = getc(cmdstream);
      if(c == 'q')
	 return 0;
      if ( c == ' ' )
	 return 1;
      if ( c == '\n' )
	 return 2;
      return 3;
   return 0;
}
```
- `tty` displays current terminal for stdin `/dev/pts/0`, `/dev/pts/1`, etc for each open terminal
- `/dev/tty` is a file that represents a terminal
    * We can open this file in read mode which reads the keyboard
