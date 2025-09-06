/*
 * target_linux.c      compiler support routines for a Linux target platform
 */

#include  <stdio.h>
#include  <stdint.h>				// defines memory sizes




#include  "TinyBasicLike.h"



#define  LINUX_VERSION_INFO		"v0.01"

const unsigned char					t_TargetIDMsg[] =
		"Linux 64-bit TinyBasicLike target " LINUX_VERSION_INFO "  20 Jul 2023  KEL";






struct  termios				oldterm;
struct  termios				newterm;
struct  itimerval			oldtimer;
struct  itimerval			newtimer;

struct  Port
{
	DATA_SIZE				portaddr;
	unsigned int			size;
};
struct Port  porttable[] =
{

};


int							OutputStream;
int							InputStream;

extern FILE					*rfp;					// use core's version of read file pointer
extern FILE					*wfp;					// use core's version of write file pointer


DATA_SIZE					*timeraddrs[T_NUM_TIMERS] = {0, 0, 0, 0};

unsigned char				t_program[T_PROGSPACE_SIZE];		// define RAM block holding entire program, stacks, and vars



/*
 * Define variables to act as virtual ports for the desktop Linux system.
 *
 * In a real embedded system, these ports would be true I/O port registers.
 */
static uint8_t					vPORTA;
static uint8_t					vPORTB;
static uint8_t					vPORTC;

static uint16_t					vPORTM;
static uint16_t					vPORTN;
static uint16_t					vPORTO;
static uint16_t					vPORTP;



/*
 * Define a table showing the names of all known ports.  Structure of this table
 * matches those of the similar tables in the core program.
 *
 * Note that the #defines for the table indexes are NOT defined here, they are defined in the
 * corresponding target_xxx.h file!  If you change the table entries here, you MUST make corresponding
 * edits in the #defines or your ports will be jumbled up or unreachable.  (Yeah, it's a lousy
 * design.)
 */
const unsigned char			ports_tab[] =
{
	"PORTA "
	"PORTB "
	"PORTC "

	"PORTM "
	"PORTN "
	"PORTO "
	"PORTP "

	"\0"
};


/*
 * Define a structure holding the memory address and size of all the declared ports.
 *
 * Since desktop Linux doesn't actually have ports, this target file uses variables as
 * pretend ports.
 *
 * Order matters!  The order of the ports defined here MUST match the entries in the
 * ports_tab[] array above!
 */
struct Port 				porttable[] =
{
	{(DATA_SIZE) &vPORTA,	8},
	{(DATA_SIZE) &vPORTB,	8},
	{(DATA_SIZE) &vPORTC,	8},

	{(DATA_SIZE) &vPORTM,	16},
	{(DATA_SIZE) &vPORTN,	16},
	{(DATA_SIZE) &vPORTO,	16},
	{(DATA_SIZE) &vPORTP,	16},
};



/*
 * local functions
 */
static void		dctimercallback(int  signum);


/*
 * local variables
 */
static int		installeddctimercallback = FALSE;



/*
 * t_ColdBoot      initial preparation following hardware reset
 *
 * For the Linux target, need to modify behavior of STDIN.  Canonical mode means calls to getchar()
 * are buffered and held until \n is entered, at which point all chars are echoed and passed to the
 * calling routine.  The Linux target needs to disable echo and disable canonical mode.
 *
 * Details on how to do this are found here:
 * https://stackoverflow.com/questions/1798511/how-to-avoid-pressing-enter-with-getchar-for-reading-a-single-character-only
 */
void			t_ColdBoot(void)
{
	tcgetattr(STDIN_FILENO, &oldterm);		// save current configuration for later use
	newterm = oldterm;						// get a working copy of current configuration
	newterm.c_lflag &= ~ECHO;				// disable echo of input char from console
	newterm.c_lflag &= ~ICANON;				// switch off canonical mode; chars are returned immediately on entry
	newterm.c_lflag &= ~ISIG;				// allow INTR, QUIT, and SUSP through
	tcsetattr(STDIN_FILENO, TCSANOW, &newterm);		// update STDIN config
	OutputStream = T_STREAM_SERIAL;			// set output stream to serial port
	InputStream = T_STREAM_SERIAL;			// set input stream to serial port
}


/*
 * t_ConsoleCharAvailable      returns TRUE if user has entered a char; does not lock
 *
 * This routine checks for available char from console, ignoring value in InputStream.
 */
int				t_ConsoleCharAvailable(void)
{
    struct timeval tv = { 0L, 0L };

    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return  select(1, &fds, NULL, NULL, &tv) > 0;
}


/*
 * t_WarmBoot      system preparation following crash of the run-time engine
 *
 * For the Linux target, set input and output streams.
 */
void			t_WarmBoot(void)
{
	OutputStream = T_STREAM_SERIAL;			// set output stream to serial port
	InputStream = T_STREAM_SERIAL;			// set input stream to serial port
}


/*
 * t_Shutdown      prepare for system shutdown, to be run before power loss
 *
 * For the Linux target, restore the functionality of STDIN.
 */
void			t_Shutdown(void)
{
	printf("\nShutting down...\n");
	tcsetattr(STDIN_FILENO, TCSANOW, &oldterm);			// restore original STDIN config
}






/*
 * t_GetCharFromConsole      get char from serial stream, ignoring value in InputStream
 *
 * This routine is used for special cases, such as break detection, where stream selection
 * via InputStream must be ignored.
 */
int				t_GetCharFromConsole(void)
{
	int					c;

	c = getchar();
	if (c == 127)  c = '\b';
	return  c;
}



/*
 * t_SetOutputStream      change character output stream
 */
int				t_SetOutputStream(int  s)
{
	if (s != T_STREAM_FILE && s != T_STREAM_SERIAL)  return  -1;

	OutputStream = s;
	return  0;
}



/*
 * t_SetInputStream      change character input stream
 */
int				t_SetInputStream(int  s)
{
	if (s != T_STREAM_FILE && s != T_STREAM_SERIAL)  return  -1;

	InputStream = s;
	return  0;
}



/*
 * dctimercallback      routine for handling timer interrupts
 *
 * This routine is called each time the timer tic rate elapses.  This
 * code updates all the down-counting timers in the local timer array.
 * The core program can test variables linked into this timer array
 * to tell when a variable has counted down to 0.
 */
static void		dctimercallback(int  signum)
{
	int				n;

	if (signum != SIGALRM)  return;

	for (n=0; n<T_NUM_TIMERS; n++)
	{
		if (timeraddrs[n])
		{
			if (*timeraddrs[n])  *timeraddrs[n] = *timeraddrs[n] - 1;
		}
	}
}



/*
 * t_SetTimerRate      assign down-counting timer tic rate in usecs
 *
 * Note that setting a timer tic rate of 0 disables the down-counting
 * timers.
 */
void			t_SetTimerRate(unsigned int  usecs)
{
	int			secs;

	newtimer.it_value.tv_sec = 0;
	newtimer.it_value.tv_usec = usecs;
	newtimer.it_interval.tv_sec = 0;
	newtimer.it_interval.tv_usec = usecs;

	setitimer(ITIMER_REAL, &newtimer, &oldtimer);
	signal(SIGALRM, dctimercallback);
}



/*
 * t_AddTImer      add a variable to the local timer list
 */
int				t_AddTimer(DATA_SIZE  *t)
{
	int				n;

	for (n=0; n<T_NUM_TIMERS; n++)
	{
		if (timeraddrs[n] == 0)
		{
			timeraddrs[n] = t;
			return  0;
		}
	}
	return  -1;							// could not add timer
}



/*
 * t_DeleteTimer      remove a variable from the local timer list
 */
int				t_DeleteTimer(DATA_SIZE  *t)
{
	int				n;

	for (n=0; n<T_NUM_TIMERS; n++)
	{
		if (timeraddrs[n] == t)
		{
			timeraddrs[n] = 0;
			return  0;
		}
	}
	return  -1;							// could not remove timer, not in list
}


/*
 * t_OpenFile      open a file for read/write
 */
FILE			*t_OpenFile(char  *name, char  *mode)
{

	if ((name == 0) && (*name == '\0'))  return  0;			// ignore illegal name

	if (*mode == 'w')
	{
		wfp = fopen(name, mode);
		return  wfp;
	}
	else if (*mode == 'r')
	{
		rfp = fopen(name, mode);
		return  rfp;
	}
	else
		return  NULL;
}



/*
 * t_CloseFile      close a file if open
 */
int			t_CloseFile(FILE  *fp)
{
	if (fp)
	{
		fflush(fp);
		fclose(fp);
	}
	return  0;
}


/*
 * Support for I/O ports
 * These are dummy ports, since a desktop Linux system has no ports.
 */
DATA_SIZE		t_ReadPort(int  index)
{
	DATA_SIZE			a;

	a = porttable[index].portaddr;
	switch  (porttable[index].size)
	{
		case  8:
		return  *(uint8_t *)a;

		case  16:
		return  *(uint16_t *)a;

		default:
		return  0;
	}
}


void			t_WritePort(DATA_SIZE  value, int  index)
{
	DATA_SIZE			a;

	a = porttable[index].portaddr;
	switch  (porttable[index].size)
	{
		case  8:
		*(uint8_t *)a = (value & 0xff);
		break;

		case 16:
		*(uint16_t *)a = (value & 0xffff);
		break;
	}
}

void		t_Test(void)
{
	printf("\nt_Test() executed.\n");
}



