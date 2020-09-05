# Lecture 14

## Directory Management Calls

- `mkdir` and `rmdir`
    * `mkdir` creates a new empty directory with two entries `.` and `..`
    * Permissions on the created director are `mode & ~umask & 0777`
    * The new directory will be owned by the effective UID of the process
    * The `rmdir` function is used to delete an empty directory
        + If the link count of the directory becomes `0` with this call, and if no other process has the directory open, the space occupied by the directory is freed
    * If one or more processes have directory open when link count reaches `0` then:
        1. The last link is removed
        2. The `.` and `..` entries are removed before the function return
        3. No new files can be created in this directory
        4. Directory is freed when the last process closes it
- `opendir`
    * `opendir()` function opens the directory specified by `dirpath` and returns a pointer to a structure of type `DIR` which is used to refer that directory in later calls
    * Upon return of `opendir()`, directory stream is positioned at the first entry in the directory list
    * `closedir()` closes directory stream associated with `dirp`
    * Directories can be read by anyone who has access permission to read the directory
        + However only the kernel can write to a directory so the write permission bits and execute permission bits for a directory determine if we can create new files in the directory and remove files from the directory
- `readdir`
    * `readdir()` dunction is passed the `DIR*` which is retruned by `opendir()`
    * Every time it is called, it returns an entry from the directory stream referred to by `dirp`
    * The return value is a pointer to a structure of type `dirent` containing the following info about the entry:
    ```
    struct dirent {
        ino_t d_ino; // File inode number
        char d_name[]; // Null terminated name of file
    }
    ```
    * This structure is overwritten on each call to `readdir()`
    * The filenames returned by `readdir()` are not in sorted order but rather in the order in which they happen to occur in the directory
        + This depends on the order in which filesystem adds files to the directory and how it fills gaps in the directory list after files are removed
        + `ls -f` lists files in the same unsorted order that they would be retrieved by `readdir()`
    * On end-of-director or error, `readdir()` returns NULL, in the latter case setting `errno` to indcate the error
    * If the contents of a directory change while a program is scanning it with `readdir()` program might not see changes
    * All filenames that have been neither added nor removed since the last such call are guaranteed to be returned
- Other functions:
    * `chdir` used to change the current working directory of calling process
    * `rewinddir` moves directory stream `dirp` back to beginning so that `readdir()` will begin with the first file in the directory
    * `telldir` returns the current location associated with the directory stream `dirp`
    * `seekdir` sets location in the directory stream from which the next `readdir()` call will start

## Example

```
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <errno.h>

extern int errno;
int main(){
   printf("Directory scan of /home/: \n");
   DIR* dp = opendir("/home");
   chdir("/home");
   errno = 0;
   struct dirent* entry;
   while(1){
      entry = readdir(dp); // Returns a structure of dirent type containing inode number and name of file and subdirectories inside the directory pointed to by dp
      if(entry == NULL && errno != 0){
         perror("readdir");
         return errno;
      }
      if(entry == NULL && errno == 0){
         printf("\nEnd of directory\n");
         return 0;
      }
      printf("%s   ",entry->d_name);
   }
   closedir(dp); // Close the directory stream
   return 0;
}
```

## Unix ls utility

- What does `ls` do?
    * Default behavior is to list contents of working directory after sorting them in alphabetical order and displaying them to stdout in columns
    * `-i` to show inode information
    * `-a` to show hidden files
    * `-R` for recursively going through each subdirectory
    * `-l` to show long listing
        + Total number of blocks taken up by files and directories (not including sub-directories)
        + File type of each file
            - `-`: regular file
            - `b`: block
            - `p`: pipe
            - `l`: softlink
            - `s`: socket
            - `d`: directory
            - `c`: character
        + Permissions for owner, group members and others
        + Link count (normally one but in case of directory is 2 + `n` where `n` is the number of subdirectories)
        + User and group
        + File size
            * Character and block shows major and minor number of driver programs instead of size
            * Pipes will always have size of zero
        + Creation time

## How does ls do it?

1. Open the directory
2. Read entry until end of directory
3. Display entry contents
4. Go to step 2
5. Close the director

## Version 1

- Receives exactly one directory name via command line argument and displays the names of files and subdirectories in the order as they appear in the directory
```
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <errno.h>

extern int errno;
void do_ls(char*);
int main(int argc, char* argv[]){
   if (argc != 2){
   printf("Enter exactly one argument (a directory name).\n");
   exit(1);
   }
   printf("Directory listing of %s:\n", argv[1] );
   do_ls(argv[1]);
   return 0;
}


void do_ls(char * dir){
   struct dirent * entry;
   // Open directory to get directory pointer
   DIR * dp = opendir(dir);
   if (dp == NULL){
      fprintf(stderr, "Cannot open directory:%s\n",dir);
      return;
   }
   errno = 0;
   # Read directory entry
   while((entry = readdir(dp)) != NULL){
      if(entry == NULL && errno != 0){
         perror("readdir failed");
         exit(errno);
      }
      else
        # Print the name parameter of the directory entry data structure
         printf("%s\n",entry->d_name);
      }
      # Close the directory pointer
      closedir(dp);
}
```

## Version 2

- Next version should display current working directory if no arguments passed into it and also handle mutiple directory input
```
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include<sys/stat.h>
#include <stdlib.h>
#include <errno.h>

extern int errno;
void do_ls(char*);
int main(int argc, char* argv[]){
    // If no arguments just use current workinf director
   if (argc == 1)
      do_ls(".");
   else{
      int i=0;
      // Go through all arguments and perform do_ls on each one
      while(++i < argc){
         printf("Directory listing of %s:\n", argv[i] );
	      do_ls(argv[i]);
      }
   }
   return 0;
}

void do_ls(char * dir)
{
   struct dirent * entry;
   DIR * dp = opendir(dir);
   if (dp == NULL){
      fprintf(stderr, "Cannot open directory:%s\n",dir);
      return;
   }
   errno = 0;
   while((entry = readdir(dp)) != NULL){
         if(entry == NULL && errno != 0){
                perror("readdir failed");
                exit(1);
         }else
                printf("%s\n",entry->d_name);
   }
   closedir(dp);
}
```

## Version 2b

- Do not display hidden files
```
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include<sys/stat.h>
#include <stdlib.h>
#include <errno.h>

extern int errno;
void do_ls(char*);
int main(int argc, char* argv[]){
   if (argc == 1){
         printf("Directory listing of pwd:\n");
      do_ls(".");
   }
   else{
      int i = 0;
      while(++i < argc){
         printf("Directory listing of %s:\n", argv[i] );
	 do_ls(argv[i]);
      }
   }

   return 0;
}


void do_ls(char * dir)
{
   struct dirent * entry;
   DIR * dp = opendir(dir);
   if (dp == NULL){
      fprintf(stderr, "Cannot open directory:%s\n",dir);
      return;
   }
   errno = 0;
   while((entry = readdir(dp)) != NULL){
         if(entry == NULL && errno != 0){
  		perror("readdir failed");
		exit(1);
  	}else{
                // If the file name starts with a . then do not display it
                if(entry->d_name[0] == '.')
                    continue;
        }     	printf("%s\n",entry->d_name);
   }
   closedir(dp);
}
```

## Version 3

- Version adds a feature that displays long listing displaying:
    1. File type, and permissions
    2. Link count
    3. User
    4. Group
    5. Size
    6. Time
    7. Name of file
- These attributes are not stored in `dirent` function which just has the inode and the name!
- `stat()` system call
    * `stat(const *char pathname, struc stat *buff)`
    * `stat()` can be used to access the file attributes stored in its inode
    * To stat a file no permissions are required on the file itself
    * However, execute permission is required on all of the directories in pathname that leads to the file
    * `stat()` stats the file pointed by `path` and fills in `buff`
    * `lstat()` is similar to `stat()` except if path is a symbolic link then the link itself is stated not the file it refers to
    * On success returns `0` and on error returns `-1` and set `errno`
    * On success populate the `stat` structre as mentioned on the next slide
- `stat` structure:
```
struct stat{
    ino_t   st_ino;   // inode number
    mode_t  stmode;   // file type and protection
    nlink_t st_nlink; // number of hard links
    uid_t   st_uid;   // user ID of owner
    gid_t   st_gid;   // group ID of owner
    off_t   st_size;  // total size in bytes
    time_t  st_atime; // time of last access
    time_t  st_mtime; // time of last data modification
    time_t  st_ctime; // time of last status change
}
```
- Program:
```
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
void show_stat_info(char*);
int main(int argc, char *argv[]){
   if(argc != 2){
      fprintf(stderr, "Incorrect number of arguments\n");
      exit(1);
   }
   show_stat_info(argv[1]);
   return 0;
}

void show_stat_info(char *fname){
   struct stat info;
   int rv = lstat(fname, &info);
   if (rv == -1){
      perror("stat failed");
      exit(1);
   }
   printf("mode: %o\n", info.st_mode);
   printf("link count: %ld\n", info.st_nlink);
   printf("user: %d\n", info.st_uid);
   printf("group: %d\n", info.st_gid);
   printf("size: %ld\n", info.st_size);
   printf("modtime: %ld\n", info.st_mtime);
   printf("name: %s\n", fname );
}
```
- Note `stat <file>` from the shell displays similar results
- Next we want to convert user and group IDs to user and group name
- `getpwuid()` system call
    * Returns a pointer to a structure containing broken-out fields of the record in the password database `/etc/passwd` that matches the supplied `uid`
    * Passwd structure is:
    ```
    struct passwd{
        char* pwd_name;
        char* pw_passwd;
        uid_t pw_uid;
        gid_t pw_gid;
        char* pw_gecos;
        char* pw_dir;
        char* pw_shell;
    }
    ```
- `getgrgid()` function returns a pointer to a structure containing the broken-out fields of the record in the group database `/etc/group` that matches the supplied `gid`
* `group` structure:
```
struct group{
    char* gr_name;
    char* gr_passwd;
    gid_t gr_grid;
    char* gr_gmem;
}
```

## Programs that receives UID/GID via command line and display corresponding user/group name

- Convert user id to name:
```
#include <stdio.h>
#include <errno.h>
#include <pwd.h>
#include <stdlib.h>

extern int errno;
int main(int argc, char* argv[]){
   if(argc != 2){
	printf("You must enter one cmd line arg, i.e., UID \n");
	exit(1);
   }
   int uid = atoi(argv[1]);
   errno = 0;
   struct passwd * pwd = getpwuid(uid);

   if (pwd == NULL){
      if (errno == 0)
         printf("Record not found in passwd file.\n");
      else
         perror("getpwuid failed");
   }
   else
       printf("Name of user is: %s\n",pwd->pw_name);
   return 0;
}
```
- Convert group id to name:
```
#include <stdio.h>
#include <errno.h>
#include <grp.h>
#include <stdlib.h>

extern int errno;
int main(int argc, char* argv[]){
   if(argc!=2){
	printf("Enter exactly one command line argument: gid\n");
	exit(1);
   }
   int gid = atoi(argv[1]);
   struct group * grp = getgrgid(gid);

   errno = 0;
   if (grp == NULL){
      if (errno == 0)
          printf("Record not found in /etc/group file.\n");
      else
          perror("getgrgid failed");
   }else
      printf("Name of group is: %s \n", grp->gr_name);
   return 0;
}
```
- Convert epoch time to date time string using `ctime`
```
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char* argv[])
{
   if (argc != 2){
      printf("usage- ./a.out n /n where n are the number of seconds.\n");
      exit(1);
   }
   long secs = atoi(argv[1]);
   printf("Date for %ld secs since epoch: %s\n",secs, ctime(&secs));
   return 0;
}
```

## Understanding st_mode member of stat()

- 16 bit `st_mode` member of `struct stat` that we received using `stat` system call contains information about file type and permissions as shown below
- Example:
    * File type
        + 1000 (unix only has 7 file types)
            - Below shows decimal, binary, octal
            - 1,  ∂∂∂, 01 = p
            - 2,  0010, 02 = c
            - 4,  0100, 04 = d
            - 6,  0110, 06 = b
            - 8,  1000, 10 = -
            - 10, 1010, 12 = l
            - 12, 1100, 14 = s
    * Special permissions
        + 000 (no special permissions i.e., suid, sgid and sticky bit)
    * User
        + 110 (read and write permissions for user)
    * Group
        + 100 (read permissions for group)
    * Others
        + 000 (no permissions for others)
- You can determine the file type by creating a mask by making all the bits zero other than the one of your interest
    * To determine the file type, you set the four bits of file type and zero out the rest of the bits
- Then you perform a bitwise `&` of the `st_mode` value with the mask and compare the output with the file codes to determine file type
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h> // if you are using constant O_RDONLY
#include <sys/stat.h>
int main(int argc, char* argv[])
{
   if(argc != 2){
      fprintf(stderr, "Incorrect number of arguments\n");
      exit(1);
   }
   struct stat buf;
   if (lstat(argv[1], &buf)<0){
      perror("Error in stat");
      exit(1);
   }
   if ((buf.st_mode &  0170000) == 0010000)
		printf("%s is a Named Pipe\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0020000)
		printf("%s is a Character Special file\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0040000)
		printf("%s is a Directory\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0060000)
		printf("%s is a Block Special file\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0100000)
		printf("%s is a Regular file\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0120000)
		printf("%s is a Soft link\n", argv[1]);
   else if ((buf.st_mode &  0170000) == 0140000)
		printf("%s is a Socket\n", argv[1]);
   else
		printf("Unknwon mode\n");

   return 0;
}
```
- You can determine the file permissions by creating a mask and making all bits zero other than the one of interest
- The you perform a bitwise `&` of the `st_mode` value with the mask and check if the specific bit for that permission is set or not
    * If it is set that means the permission is on otherwise it is off
- Example:
```
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc, char* argv[]){
   if(argc != 2){
      fprintf(stderr, "Incorrect number of arguments\n");
      exit(1);
   }
   struct stat buf;
   if (lstat(argv[1], &buf)<0){
      perror("Error in stat");
      exit(1);
   }
   int mode = buf.st_mode;
   char str[10];
   strcpy(str, "---------");
//owner  permissions
   if((mode & 0000400) == 0000400) str[0] = 'r';
   if((mode & 0000200) == 0000200) str[1] = 'w';
   if((mode & 0000100) == 0000100) str[2] = 'x';
//group permissions
   if((mode & 0000040) == 0000040) str[3] = 'r';
   if((mode & 0000020) == 0000020) str[4] = 'w';
   if((mode & 0000010) == 0000010) str[5] = 'x';
//others  permissions
   if((mode & 0000004) == 0000004) str[6] = 'r';
   if((mode & 0000002) == 0000002) str[7] = 'w';
   if((mode & 0000001) == 0000001) str[8] = 'x';
//special  permissions
   if((mode & 0004000) == 0004000) str[2] = 's';
   if((mode & 0002000) == 0002000) str[5] = 's';
   if((mode & 0001000) == 0001000) str[8] = 't';
   printf("%s\n", str);
   return 0;
}
```