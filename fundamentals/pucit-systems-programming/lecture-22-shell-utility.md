# Lecture 22

## What does a Shell do?

- Execute commands
- Job control
- Name completion
- Maintains history of cmmands
- Perform I/O redirection
- Use of pipes `|`
- Shell variables (env and user defined)
- Shell operators (arithmetic, comparison, logical, file)
- Programming ability (if..else and loops)

## Types of shells

- `man bash`
- `man sh`
- `man csh`
- `man tcsh`
- `man ksh`
- `man zsh`
- `ps -l q $$` shows we are running bash shell
- Shell is an interactive proogram for executing other proograms
- `ls; date; pwd` too execute multiple commands
- Shell can execute a shell script and execute statements in sequence
- Internal commands are part of the shell
    * Example: `history`, `bg`, etc
    * `compgen -b` to list internal commands logged in user can execute
- External commands
    * `type -a <command>`
    * Some commands have both internal and external
    * To execute external, must give full path
    * Shell spawns child process and overwrites it with `exec()` system call
    * `compgen -c` to list external commands
- `sleep 1000 &` runs in background
- `fg %1` to send it back to fooreground
- `bg %1` to send it back to background
    * Note: `1` is the jobid
- Shell does name completion for executable and file names
- `history` shows previous histories kept in memory
    * `~/.bash_history`
    * `!!` to run previous command
- `cat 0< /etc/passwd 1> op.txt 2> err.txt`
    * Attach stdin with `/etc/passwd`
    * Attach stdout with `op.txt`
    * Attach stderr with `err.txt`
- `gunzip 0< /usr/share/man/m1/ls.1.gz | cat | grep ls`
    * `gunzip` reads input and sends output to `cat` via pipe
    * `cat` sends output to `grep` via pipe
- `set | less` to view env vars
- `name="Arif Butt"` to set local var for current shell only
- `echo Learning is fun with $name` too access previous variable
- `expr 5 + 4` to use arithmetic operations
- `[ 5 -ne 6 ]; echo $?` to use numerical comparison operators
- `[ arif = rauf ]; echo $?` to use string comparison operators
- `true && false; echo $?`  to use logical operators
- `[ -f /etc/passwd ]; echo $?` to use file operators
- `if [ -f /etc/passwd ]; then echo passwd is a file]` to use programability
- `for ctr in 1 2 3 4 5; do echo $ctr done`  to use control structure

## How dooes the shell do it

1. Display prompt
2. Read command line string
3. Tokenizes it
4. If control command then handles it
5. If internal command executes its code
6. If external command
    * Child process is forked, and `exec` with the command
    * Parent process `wait` for termination of the child
7. After child terminates, parent process go to step 1

## Tokenizing the Command Sting

- Example `cat /etc/passwd`
    * 0 becomes `c a t \0`
    * 1 becomes `/ e t c / p a s s w d \0`
    * 2 becomes `\0`
- Example using `execvp` passing in executable and arguments
```
#include <stdio.h>
#include <unistd.h>
int main(){
   char	*arglist[4];
   arglist[0] = "ls";
   arglist[1] = "-l";
   arglist[2] = "/home";
   arglist[3] = NULL;
   execvp(arglist[0], arglist);
   return 0;
}
```
- Example
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main(){
 printf("You must enter only a command and one argument:\n");
    // Allocate three strings of ten bytes on heap
   char *arglist[3];
   for(int i =0; i< 3; i++)
      arglist[i] = (char*)malloc(sizeof(char)*10);

   printf("arglist[0]: ");
   scanf("%s", arglist[0]);
   printf("arglist[1]: ");
   scanf("%s", arglist[1]);
   arglist[2] = NULL;
   execvp(arglist[0], arglist);
   perror("Exec failed");
   return 0;
}
```
- Example of above with more than one arguments:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(){
   int maxargs;
   printf("How many arguments you want to enter(including the cmd): ");
   scanf("%d", &maxargs);
   char	**arglist = (char**)malloc(sizeof(char*)* (maxargs+1));
   for(int i =0; i< maxargs+1; i++)
      arglist[i] = (char*)malloc(sizeof(char)*10);

   int i =0;
   while(i<maxargs){
      printf("arglist[%d]: ", i);
      scanf("%s", arglist[i]);
      i++;
   }
   arglist[i] = NULL;
   execvp(arglist[0], arglist);
   perror("Exec failed");
   return 0;
}
```
- Example to enter any command without specifying number of arguments:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_LEN 512
#define MAXARGS 10
#define ARGLEN 30

char* read_cmd(FILE*);
char** tokenize(char* cmdline);
int main(){
   printf("Enter a command of your choice:- ");
   char *cmdline;
   cmdline = read_cmd(stdin);
   char** arglist = tokenize(cmdline);
   execvp(arglist[0], arglist);
   perror("Exec failed");
   return 0;
}
//this function gets character by character input, creates and returns a string
char* read_cmd(FILE* fp){
   int c; //input character
   int pos = 0; //position of character in cmdline
   char* cmdline = (char*) malloc(sizeof(char)*MAX_LEN);
   while((c = getc(fp)) != EOF){
      if(c == '\n')
         break;
      cmdline[pos++] = c;
   }
   cmdline[pos] = '\0';
   return cmdline;
}

char** tokenize(char* cmdline){
    // Allocates memory for 10 words each of ARGLEN (30 bytes)
   char** arglist = (char**)malloc(sizeof(char*)* (MAXARGS+1));
   for(int i=0; i < MAXARGS+1; i++){
	   arglist[i] = (char*)malloc(sizeof(char)* ARGLEN);
      bzero(arglist[i],ARGLEN);
   }
   char* cp = cmdline; // pos in string
   char* start;
   int len;
   int argnum = 0; //slots used
   while(*cp != '\0'){
      while(*cp == ' ' || *cp == '\t') //skip leading spaces
          cp++;
      start = cp; //start of the word
      len = 1;   //initialize length of the word to 1
      //find the end of the word
      while(*++cp != '\0' && !(*cp ==' ' || *cp == '\t'))
              len++;
      strncpy(arglist[argnum], start, len);
      arglist[argnum][len] = '\0';
      argnum++;
   }
   arglist[argnum] = NULL;
   return arglist;
}
```
- Use above concepts to create shell:
```

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LEN 512
#define MAXARGS 10
#define ARGLEN 30
#define PROMPT "PUCITshell:- "

int execute(char* arglist[]);
char** tokenize(char* cmdline);
char* read_cmd(char*, FILE*);
int main(){
   char *cmdline;
   char** arglist;
   char* prompt = PROMPT;
   while((cmdline = read_cmd(prompt,stdin)) != NULL){
      if((arglist = tokenize(cmdline)) != NULL){
            execute(arglist);
       //  need to free arglist
         for(int j=0; j < MAXARGS+1; j++)
	         free(arglist[j]);
         free(arglist);
         free(cmdline);
      }
  }//end of while loop
   printf("\n");
   return 0;
}
int execute(char* arglist[]){
   int status;
   int cpid = fork();
   switch(cpid){
      case -1:
         perror("fork failed");
	      exit(1);
      case 0:
	      execvp(arglist[0], arglist);
 	      perror("Command not found...");
	      exit(1);
      default:
	      waitpid(cpid, &status, 0);
         printf("child exited with status %d \n", status >> 8);
         return 0;
   }
}
char** tokenize(char* cmdline){
//allocate memory
   char** arglist = (char**)malloc(sizeof(char*)* (MAXARGS+1));
   for(int j=0; j < MAXARGS+1; j++){
	   arglist[j] = (char*)malloc(sizeof(char)* ARGLEN);
      bzero(arglist[j],ARGLEN);
    }
   if(cmdline[0] == '\0')//if user has entered nothing and pressed enter key
      return NULL;
   int argnum = 0; //slots used
   char*cp = cmdline; // pos in string
   char*start;
   int len;
   while(*cp != '\0'){
      while(*cp == ' ' || *cp == '\t') //skip leading spaces
          cp++;
      start = cp; //start of the word
      len = 1;
      //find the end of the word
      while(*++cp != '\0' && !(*cp ==' ' || *cp == '\t'))
         len++;
      strncpy(arglist[argnum], start, len);
      arglist[argnum][len] = '\0';
      argnum++;
   }
   arglist[argnum] = NULL;
   return arglist;
}

char* read_cmd(char* prompt, FILE* fp){
   printf("%s", prompt);
  int c; //input character
   int pos = 0; //position of character in cmdline
   char* cmdline = (char*) malloc(sizeof(char)*MAX_LEN);
   while((c = getc(fp)) != EOF){
       if(c == '\n')
	  break;
       cmdline[pos++] = c;
   }
//these two lines are added, in case user press ctrl+d to exit the shell
   if(c == EOF && pos == 0)
      return NULL;
   cmdline[pos] = '\0';
   return cmdline;
}
```