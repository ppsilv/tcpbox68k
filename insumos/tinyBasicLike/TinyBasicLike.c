/*
 * TinyBasicLike      a target-independent version built from TinyBasicPlus
 * 
 * See the long chain of history notes immediately below.
 * 
 * I built tbl on the core of TinyBasicPlus just for the fun of making a small
 * Basic interpreter that was as target-independent as possible.  I doubt it will
 * ever be used by more than a dozen people, if that, but it seemed like a fun
 * project, so why not?
 * 
 * I started my project using TinyBasicPlus version 0.15, pulled from here:
 * https://github.com/BleuLlama/TinyBasicPlus
 * 
 * Note that BleuLlama's version targets Arduino; mine is wide open and can target
 * anything.  Targeting a particular board requires writing a small C file containing
 * target-specific routines, then compiling that file with this one and a suitable
 * linker script.
 * 
 * For example, to build a Linux version, you would need to create a target_linux.c
 * file and add the appropriate character I/O routines (as a minimum).  You would also
 * need to make a matching target_linux.h file with the function prototypes and any
 * needed definitions.  Finally, rebuild.
 * 
 * Assuming you named your Linux target file target_linux.c, the build command would
 * be: gcc -o tbl TinyBasicLike.c target_linux.c
 * 
 * 
 * Karl Lunt   4 Jul 2023
 */
 

////////////////////////////////////////////////////////////////////////////////
// TinyBasic Plus
////////////////////////////////////////////////////////////////////////////////
//
// Authors: 
//    Gordon Brandly (Tiny Basic for 68000)
//    Mike Field <hamster@snap.net.nz> (Arduino Basic) (port to Arduino)
//    Scott Lawrence <yorgle@gmail.com> (TinyBasic Plus) (features, etc)
//
// Contributors:
//          Brian O'Dell <megamemnon@megamemnon.com> (INPUT)
//    (full list tbd)

//  For full history of Tiny Basic, please see the wikipedia entry here:
//    https://en.wikipedia.org/wiki/Tiny_BASIC

// LICENSING NOTES:
//    Mike Field based his C port of Tiny Basic on the 68000 
//    Tiny BASIC which carried the following license:
/*
******************************************************************
*                                                                *
*               Tiny BASIC for the Motorola MC68000              *
*                                                                *
* Derived from Palo Alto Tiny BASIC as published in the May 1976 *
* issue of Dr. Dobb's Journal.  Adapted to the 68000 by:         *
*       Gordon Brandly                                           *
*       12147 - 51 Street                                        *
*       Edmonton AB  T5W 3G8                                     *
*       Canada                                                   *
*       (updated mailing address for 1996)                       *
*                                                                *
* This version is for MEX68KECB Educational Computer Board I/O.  *
*                                                                *
******************************************************************
*    Copyright (C) 1984 by Gordon Brandly. This program may be   *
*    freely distributed for personal use only. All commercial    *
*                      rights are reserved.                      *
******************************************************************
*/
//    ref: http://members.shaw.ca:80/gbrandly/68ktinyb.html
//
//    However, Mike did not include a license of his own for his
//    version of this.  
//    ref: http://hamsterworks.co.nz/mediawiki/index.php/Arduino_Basic
//
//    From discussions with him, I felt that the MIT license is
//    the most applicable to his intent.
//
//    I am in the process of further determining what should be
//    done wrt licensing further.  This entire header will likely
//    change with the next version 0.16, which will hopefully nail
//    down the whole thing so we can get back to implementing
//    features instead of licenses.  Thank you for your time.



#define  tblVersion		"v0.03  22 Jul 2023  KEL"
/*
 * v0.03:  22 Jul 2023  KEL
 * 		Message following break now shows active line number when break occurred.
 * 		Added LOCK to lock range of line numbers to prevent editing of program.
 * 		Added UNLOCK to remove editing lock.
 * 		Added ShowProgramLockState() to report program editing lock state.
 * 		Added REBOOT command to force a soft reboot of the system.  This does NOT
 * 			perform a hardware reset; it only restarts the interpreter and calls
 * 			the target t_ColdBoot() and t_WarmBoot() functions.  (CHANGED!  See below.)
 * 		Sorry, What?, and How? messages now show offending line number.
 * 		Added OUTCHAR keyword; sends following value as an ASCII char to output.
 * 		Added BEEP keyword to trigger a fixed duration tone, if target supports such.
 * 		Rearranged #defines for declaring program space and size to allow the target
 * 			to define required RAM space based on flash file support.
 * 		Fixed code in printum() that didn't handle hex output properly; this meant a
 * 			rewrite of the hex code to avoid undefined behavior during long right-shifts.
 * 		Code in expr4() now throws an error on any illegal chars during parsing.
 * 		Replaced isxdigit() and isdigit() with macros __isxdigit() and __isdigit().  The
 * 			original functions are part of newlib and adding newlib support is more work
 * 			than it's worth.
 * 		Added $ as a macro for current line:  500 if n > 0 goto $
 * 		Added FLSAVE keyword; invokes t_ForceWriteToFlash (if supported) to write RAM
 * 			buffer to flash.  This is an alternate method to force a flash save without
 * 			using BYE.
 * 		Changed functionality of REBOOT command.  It now forces a hardware reset by
 * 			calling the target's t_ForceHWReset() function.  REBOOT cannot be used
 * 			inside a program.
 * 
 * v0.02:  11 Jul 2023  KEL
 * 		Added AND, OR, and XOR logical operators.
 * 		Added NOT as unary logical negation (10 c = not b)
 * 		Added support for target-defined ports; ports can be any size (8, 16, 32 bits).
 * 		Ports are defined by the target and provided to the core as a table of port
 * 		   names.
 * 		Now uses t_ReadPort() to read data from a named port.
 * 		Now uses t_WritePort() to write data to a named port.
 * 		Added ports to list of elements printed by WORDS.
 * 		Moved ADDTIMER and DELTIMER to keyword list; didn't work well as functions.
 * 		Added >> and << shift operators; also added to displayed WORDS as shift operators.
 * 		Now calls target's t_GetFirstFileName() and t_GetNextFileName() to support
 * 		   FILES command.  NOTE: This is not POSIX-compliant and won't work immediately with
 * 		   a Linux target.
 * 		Added DELETE command to delete a named file.
 * 		Removed DELAY command, it has been replaced with the non-locking ADDTIMER
 * 		   functionality.
 * 		Rewrote RND() function to use 64-bit custom RNG code, scaled by DATA_SIZE.
 * 		Updated code for '\' comments; these comments are no longer changed to uppercase.
 * 		Overloaded the '=' assignment operator to allow initializing multiple array
 * 		   elements in one statement.
 * 		Trying to overwrite a program in RAM now gives an Are You Sure? prompt; user
 * 		   must respond with 'y' or 'Y' to allow the overwrite.
 * 		main() now displays the target's ID string on startup.
 * 		Now supports pressing blue USER pushbutton to generate hardware break; works same
 * 		   as pressing ctrl-C on console.
 * 		Now supports automatic execution of file named autorun.bas (case-sensitive!) on
 * 		   startup, if such file exists in flash.
 * 		Rewrote the INPUT keyword code; my first try was too clumsy and hard to follow.
 * 		Rewrote the WORDS keyword code; heavy use of printmsg() makes it simpler.
 * 		Added printstr() function to allow printing double-quoted strings as an
 * 		    argument; this removed compiler warnings when using printmsg() to print
 * 			quoted strings.
 * 		Lots of code cleanup to remove compiler warnings.  Most involved changing
 *		    'unsigned char' to 'char'; this may bite me later...
 * 
 * v0.01:  10 Jul 2023  KEL
 * 		Removed all #ifdef blocks, isolating target-independent
 * 		   functionality in this program and target-specific functionality
 * 		   in associated target_xxx.c file.
 * 		Size (in bits) of a data element is now declared by target, not core; see
 * 		   DATA_SIZE.  This allows creation of a 64-bit TinyBasic.  :-)
 * 		Variables X, Y, and Z expanded to be 2D arrays; currently 20x20 cells.
 * 		Variables X, Y, and Z can be used as single-cell vars, 1D arrays, or
 * 		   2D arrays.
 * 		INPUT now accepts hex (0x) values.
 * 		INPUT now accepts char ('c') values.
 * 		PRINTX and ?X added to output values in hex
 * 		PRINTA and ?A added to output values as ASCII chars
 * 		ADDR() function added to return address of a variable or cell within
 * 		    an array.
 * 		Modified file support so all file operations occur in target code.
 * 		LOAD and NEW now warn that program is about to be erased, user must
 * 		    verify action.
 * 		MERGE keyword added to merge program from file with current program.
 * 		ADDTIMER() function added to add a down-counting timer to target-maintained
 * 		    timer list.
 * 		DELTIMER() function added to remove a down-counting time from target-
 * 		    maintained timer list.
 * 		TIMERRATE keyword added to specify tic rate (in usecs) for use by target.
 * 		LIST modified to allow listing one line, all lines, or a range of lines.
 * 		SAVE modified to allow saving one line, all lines, or a range of lines.
 * 		WORDS keyword added to list all keywords, function names, and relational
 * 		    operators to console.
 * 		Fixed bug in RND() function that crashed if no function argument was provided.
 */

/////////////////////////////////////////////////////////////////

//#define kVersion "v0.15"

// v0.15: 2018-06-23
//      Integrating some contributions
//      Corrected some of the #ifdef nesting atop this page
//      Licensing issues beginning to be addressed

// v0.14: 2013-11-07
//      Modified Input command to accept an expression using getn()
//      Syntax is "input x" where x is any variable
//      NOTE: This only works for numbers, expressions. not strings.
//
// v0.13: 2013-03-04
//      Support for Arduino 1.5 (SPI.h included, additional changes for DUE support)
//
// v0.12: 2013-03-01
//      EEPROM load and save routines added: EFORMAT, ELIST, ELOAD, ESAVE, ECHAIN
//      added EAUTORUN option (chains to EEProm saved program on startup)
//      Bugfixes to build properly on non-arduino systems (PROGMEM #define workaround)
//      cleaned up a bit of the #define options wrt TONE
//
// v0.11: 2013-02-20
//      all display strings and tables moved to PROGMEM to save space
//      removed second serial
//      removed pinMode completely, autoconf is explicit
//      beginnings of EEPROM related functionality (new,load,save,list)
//
// v0.10: 2012-10-15
//      added kAutoConf, which eliminates the "PINMODE" statement.
//      now, DWRITE,DREAD,AWRITE,AREAD automatically set the PINMODE appropriately themselves.
//      should save a few bytes in your programs.
//
// v0.09: 2012-10-12
//      Fixed directory listings.  FILES now always works. (bug in the SD library)
//      ref: http://arduino.cc/forum/index.php/topic,124739.0.html
//      fixed filesize printouts (added printUnum for unsigned numbers)
//      #defineable baud rate for slow connection throttling
//e
// v0.08: 2012-10-02
//      Tone generation through piezo added (TONE, TONEW, NOTONE)
//
// v0.07: 2012-09-30
//      Autorun buildtime configuration feature
//
// v0.06: 2012-09-27
//      Added optional second serial input, used for an external keyboard
//
// v0.05: 2012-09-21
//      CHAIN to load and run a second file
//      RND,RSEED for random stuff
//      Added "!=" for "<>" synonym
//      Added "END" for "STOP" synonym (proper name for the functionality anyway)
//
// v0.04: 2012-09-20
//      DELAY ms   - for delaying
//      PINMODE <pin>, INPUT|IN|I|OUTPUT|OUT|O
//      DWRITE <pin>, HIGH|HI|1|LOW|LO|0
//      AWRITE <pin>, [0..255]
//      fixed "save" appending to existing files instead of overwriting
// 	Updated for building desktop command line app (incomplete)
//
// v0.03: 2012-09-19
//	Integrated Jurg Wullschleger whitespace,unary fix
//	Now available through github
//	Project renamed from "Tiny Basic in C" to "TinyBasic Plus"
//	   
// v0.02b: 2012-09-17  Scott Lawrence <yorgle@gmail.com>
// 	Better FILES listings
//
// v0.02a: 2012-09-17  Scott Lawrence <yorgle@gmail.com>
// 	Support for SD Library
// 	Added: SAVE, FILES (mostly works), LOAD (mostly works) (redirects IO)
// 	Added: MEM, ? (PRINT)
// 	Quirk:  "10 LET A=B+C" is ok "10 LET A = B + C" is not.
// 	Quirk:  INPUT seems broken?

// IF testing with Visual C, this needs to be the first thing in the file.
//#include "stdafx.h"

//  ----------------  End of original TinyBasicPlus documentation  ---------------
//





#include  <stdio.h>
#include  <stdlib.h>
//#include  <ctype.h>
#include  <string.h>

/*
 * Include the appropriate target header file here.  For example, a header file for a Linux
 * target might be named target_linux.h.
 * 
 * The file name must be passed as a double-quoted string within a macro named
 * TARGET_MCU_HEADER_FILE.  For example, to include the header file target_LPC1768.h
 * as the target MCU header file, your .mak file should include:
 * 
 *    TARGET_MCU_HEADER_FILE = "target_LPC1768.h"
 *    BUILD_SPECIFIC_COMPILER_FLAGS += -D'TARGET_MCU_HEADER_FILE=$(TARGET_MCU_HEADER_FILE)'
 *    GCFLAGS += $(BUILD_SPECIFIC_COMPILER_FLAGS)
 */
#include  "m68000.h"		/* this macro MUST be defined in your make file! */
#include  "TinyBasicLike.h"



#ifndef boolean 
#define boolean		int
#endif

#ifndef byte
typedef unsigned char		byte;
#endif

/*
 * The following macros replace the newlib isdigit() and isxdigit()
 * library functions.  I use these because I can't be bothered tracking
 * down the newlib libraries when I'm porting this code to a different
 * MCU.
 * 
 * Note that these macros assume any alpha argument is already uppercase!
 */
#define  __isdigit(c)		((c>='0' && c <='9'))
#define  __isxdigit(c)		((__isdigit(c)) || ((c>='A' && c<='F')))


/*
 * Target-specific definitions that must be known to TinyBasicLike core.
 *
 * These are defined and declared in the target file and defined here as
 * externs.
 */
extern const unsigned char			t_TargetIDMsg[];


// some settings based things

boolean inhibitOutput = FALSE;
static boolean runAfterLoad = FALSE;
static boolean triggerRun = FALSE;



////////////////////////////////////////////////////////////////////////////////
// ASCII Characters
#define CR	'\r'
#define NL	'\n'
#define LF      0x0a
#define TAB	'\t'
#define BELL	'\b'
#define SPACE   ' '
#define SQUOTE  '\''
#define DQUOTE  '\"'
#define MIDEOL	':'				// mid-line eof-of-line, separates statements
#define CTRLC	0x03
#define CTRLH	0x08
#define CTRLS	0x13
#define CTRLX	0x18

/*
 * Define the char to use for current line-number.
 * For example, if CHAR_CURRENT_LINENUM is '$', this allows:
 *     200 if n > 0 goto $
 */
#define  CHAR_CURRENT_LINENUM			'$'

 


//typedef short unsigned LINENUM;
typedef uint16_t			LINENUM;		/* redefined to limit explicitly to 16 bits */


/*
 * Define a macro to mark the program as unlocked for editing.  This value must
 * be greater than the highest legal line number, which is 65534 (0xfffe).
 */
#define  BEYOND_VALID_LINENUM			(0xffff)

#define ECHO_CHARS 0


/*
 * Define variables for handling lock range line numbers
 */
 LINENUM				lockrangestart;
 LINENUM				lockrangeend;
 
 				
/*
 * Definitions of memory elements
 */
extern unsigned char		t_program[TOTAL_RAM_REQUIRED];	// program RAM buffer defined by target


static unsigned char 		*txtpos;
static unsigned char		*list_line;
static unsigned char		*tmptxtpos;
static unsigned char 		expression_error;
static unsigned char 		*tempsp;
static unsigned char		forcereboot;			// TRUE forces a soft reboot after REBOOT command
static char					tempfilename[MAX_LEN_FILENAME+1];



/*
 * General-purpose definitions
 */
#define  BEEP_FREQ			880
#define  BEEP_DURATION		150


/***********************************************************/

/*
 * Tables of words known to the core.
 * 
 * These are keywords and operators stored in lookup tables as a single,
 * space-delimited string.
 * 
 * The routine scantable() will step through each table looking for a match
 * between a string of chars in the input stream and a table entry.
 */

#define  ENTRY_NOT_FOUND			255		/* flag showing entry was not found */


const static unsigned char	keywords[] =
{
	"LIST "
	"LOAD "
	"MERGE "
	"NEW "
	"RUN "
	"SAVE "
	"FLSAVE "				// force write of RAM disc to flash
	"NEXT "
	"LET "
	"IF "
	"GOTO "
	"GOSUB "
	"RETURN "
	"REM "					// start of comment; ignore rest of line
	"FOR "
	"INPUT "
	"PRINTX "				// print data in hex
	"PRINTA "				// print low byte of data as ASCII char
	"PRINT "
	"POKE "
	"STOP "
	"BYE "
	"FILES "				// list all files in directory
	"DELETE "				// delete a file by name
	"MEM "
	"?X "					// print data in hex
	"?A "					// print low byte of data as ASCII char
	"? "
	"\\ "					// \ is same as REM; ignore rest of line
	"AWRITE "
	"DWRITE "
	"END "
	"RSEED "
	"CHAIN "
	"WORDS "				// print this list and other defined words
	"TIMERRATE "			// sets tic rate of down-counting timers, in usecs
	"ADDTIMER "				// adds a variable (by address) to timer group
	"DELTIMER "				// removes a variable (by address) from timer group
	"TONE "					// start/stop a tone; sets freq, duration, optional timer
	"LOCK? "				// report the lock state of the program
	"LOCK "					// lock all or part of current program to prevent editing
	"UNLOCK "				// unlock all of current program to allow editing
	"REBOOT "				// performs a hardware reset of the system
	"OUTCHAR "				// outputs a value as an ASCII char
	"BEEP "					// fixed freq and duration beep, blocks until tone ends
	"TEST "					// triggers a target-specific test, if available
	"\0",					// marks end of table!
};

// by moving the command list to an enum, we can easily remove sections 
// above and below simultaneously to selectively obliterate functionality.
enum {
  KW_LIST = 0,
  KW_LOAD,							// load program from file, overwriting current program (if any)
  KW_MERGE,							// merge program from file with current program (if any)
  KW_NEW,							// just prints a warning, need to use NEW! instead
  KW_RUN, KW_SAVE,
  KW_FLSAVE,
  KW_NEXT, KW_LET, KW_IF,
  KW_GOTO, KW_GOSUB, KW_RETURN,
  KW_REM,
  KW_FOR,
  KW_INPUT,
  KW_PRINTX,
  KW_PRINTA,
  KW_PRINT,
  KW_POKE,
  KW_STOP, KW_BYE,
  KW_FILES,
  KW_DELETE,
  KW_MEM,
  KW_QMARKX,
  KW_QMARKA,
  KW_QMARK,
  KW_QUOTE,
  KW_AWRITE, KW_DWRITE,
  KW_END,
  KW_RSEED,
  KW_CHAIN,
  KW_WORDS,
  KW_TIMERRATE,
  KW_ADDTIMER,
  KW_DELTIMER,
  KW_TONE,
  KW_LOCKQ,
  KW_LOCK,
  KW_UNLOCK,
  KW_REBOOT,
  KW_OUTCHAR,
  KW_BEEP,
  KW_TEST,
//  KW_DEFAULT /* always the final one*/
};


const static unsigned char		func_tab[] =
{
	"PEEK "
	"ABS "
	"AREAD "
	"DREAD "
	"RND "
	"ADDR "						// returns address of a variable or array element
	"TONE? "					// returns TRUE if tone is still active, else FALSE
	"\0"						// marks end of table!
};

enum  func_index				// order and index of enums MUST match entries in func_tab[]!
{
	FUNC_PEEK = 0,
	FUNC_ABS,
	FUNC_AREAD,
	FUNC_DREAD,
	FUNC_RND,
	FUNC_ADDR,
	FUNC_TONEQ,
//	FUNC_UNKNOWN,
}; 


const static unsigned char		to_tab[] =
{
	"TO "
	"\0"						// marks end of table!
};

const static unsigned char 		step_tab[] =
{
	"STEP "
	"\0"						// marks end of table!
};

const static unsigned char 		relop_tab[] =
{
	">= "
	"<> "
	"> "
	"= "
	"<= "
	"< "
	"!= "
	"\0"						// marks end of table
};

#define RELOP_GE		0
#define RELOP_NE		1
#define RELOP_GT		2
#define RELOP_EQ		3
#define RELOP_LE		4
#define RELOP_LT		5
#define RELOP_NE_BANG	6
//#define RELOP_UNKNOWN	7


const static unsigned char		logicop_tab[] =
{
	"AND "						// and
	"OR "						// or
	"XOR "						// exclsive-or
	"NOT "						// logical negation
	"\0"						// marks end of table
};

#define LOGICOP_AND				0
#define LOGICOP_OR				1
#define LOGICOP_XOR				2
#define LOGICOP_NOT				3
//#define LOGICOP_UNKNOWN			4


const static unsigned char		shiftop_tab[] =
{
	"<< "						// left-shift
	">> "						// right-shift
	"\0"						// marks end of table
};

#define  SHIFT_LEFT				0
#define  SHIFT_RIGHT			1



#if 0
const static unsigned char 		highlow_tab[] =
{
	"HIGH "
	"HI "
	"LOW "
	"LO"
	"\0"						// marks end of table
};

#define HIGHLOW_HIGH    1
//#define HIGHLOW_UNKNOWN 4

#endif		// if 0


static unsigned char *stack_limit;
static unsigned char *variables_begin;
static unsigned char *current_line;

unsigned char *program_start;			// allow access by target
unsigned char *program_end;				// allow access by target


/*
 * Declare a stack used solely for formatting numbers for output
 */
//#define  MAXCHARSTACKSIZE			50
//static unsigned char				charstack[MAXCHARSTACKSIZE];
static unsigned char				*stackptr;


#define STACK_GOSUB_FLAG		'G'
#define STACK_FOR_FLAG			'F'

static unsigned char table_index;
static LINENUM linenum;

static const unsigned char okmsg[]            = "OK\n";
static const unsigned char whatmsg[]          = "What? ";
static const unsigned char howmsg[]           =	"How? ";
static const unsigned char sorrymsg[]         = "Sorry ";
static const unsigned char initmsg[]          = "\nTinyBasicLike core " tblVersion "\n";
static const unsigned char memorymsg[]        = " bytes free.\n";
static const unsigned char breakmsg[]         = "Break at line ";
static const unsigned char unimplimentedmsg[] = "Unimplemented!\n";
static const unsigned char keywordsmsg[]		= "Keywords: ";
static const unsigned char functionsmsg[]		= "Functions: ";
static const unsigned char relopsmsg[]			= "Relational operators: ";
static const unsigned char logicopsmsg[]		= "Logical operators: ";
static const unsigned char shiftopsmsg[]		= "Shift operators: ";
static const unsigned char portsmsg[]			= "Ports: ";
//static const unsigned char indentmsg[]        = "    ";
//static const unsigned char sderrormsg[]       = "SD card error.";
//static const unsigned char sdfilemsg[]        = "SD file error.";
//static const unsigned char dirextmsg[]        = "(dir)";
//static const unsigned char slashmsg[]         = "/";
//static const unsigned char spacemsg[]         = " ";
static const unsigned char AreYouSureMsg[]		= "Are you sure? ";
static const unsigned char EraseWarning[]		= "This will erase existing program!  ";
static const unsigned char overwritesavedfilemsg[] = "This will overwrite existing file!  ";
static const unsigned char programunlocked[]	= "Program is unlocked for editing.\n";
static const unsigned char noprograminmemory[]	= "No program in memory.\n";



static int					inchar(void);
static void					outchar(unsigned char c);
static DATA_SIZE			expression(void);
static unsigned char		breakcheck(void);


//static char     			*filenameWord(void);
static DATA_SIZE			filenameWord(void);		// rewritten
static int					isValidFnChar(char  c);
//static char					*filename;

//FILE					*rfp;			// used for file input, such as LOAD
//FILE					*wfp;			// used for file output, such as SAVE

#define  INITIAL_RANDOM_SEED			12345

static DATA_SIZE			z1 = INITIAL_RANDOM_SEED;		// used by MyRandom() routine
static DATA_SIZE			z2 = INITIAL_RANDOM_SEED;		// used by MyRandom() routine
static DATA_SIZE			z3 = INITIAL_RANDOM_SEED;		// used by MyRandom() routine
static DATA_SIZE			z4 = INITIAL_RANDOM_SEED;		// used by MyRandom() routine



/*
 * global functions
 */
void			printmsg(const unsigned char *msg);  // prints str from const
void			printstr(char  *str);		 		 // prints str from RAM

/*
 * local functions
 */
static DATA_SIZE				*CalcAddressOfVariable(void);
static int						AreYouSure(void);
static DATA_SIZE				MyRandom(void);

void t_OutChar( char ch )
{
    printf( "%c", ch );
}

char t_GetChar()
{
	return getchar();
}
/*
 * CalcAddressOfVariable      returns address of the variable passed by char
 * 
 * Argument c is an ASCII letter from 'A' to 'Z' for the variable of interest.
 * This routine returns the address RAM of that variable.
 * 
 * Variables X, Y, and Z are assumed to be 2D arrays of ARRAY_X_SIZE *
 * ARRAY_Y_SIZE cells.  If the variable passed is X, Y, or Z, this routine
 * will check for and process any array cell information and return the
 * address of the requested cell.  Array cell numbers are zero-based.
 * 
 * For example:
 * X				returns base address of the X array
 * X(0)				returns base address of the X array
 * X(5)				returns address of the sixth element in the X array
 * X(199)			returns address of last element in the X array
 * X(5,3)			returns address of cell (5*ARRAY_X_SIZE) + 3 
 * 
 * Upon entry, txtpos points to the variable letter (A-Z).
 * 
 * Upon exit, txtpos points to the character with the last array
 * information.  If no array info was found, this will be the character
 * following the variable letter.  If array info was found, this will be
 * the character following the closing parens.
 */
static DATA_SIZE				*CalcAddressOfVariable(void)
{
	DATA_SIZE			*addr;
	int					offset;
	int					c;
	DATA_SIZE			x;
	DATA_SIZE			y;
	int					hasxyinfo;
	
	if (*txtpos < 'A' || *txtpos > 'Z')  return  0;			// oops, don't belong here
	if (expression_error)				 return  0;			// if already an error, ignore
	
	c = *txtpos;					// remember variable letter
	txtpos++;						// need to look for array info
	
	addr =  ((DATA_SIZE *)variables_begin) + (c-'A');		// calc base addr of variable
	if (c >= 'A' && c <= 'W')  return  addr;
	if (*txtpos != '(')  return addr;
	
	/*
	 * Variable is X, Y, or Z and has array info.
	 */
	x = 0;
	y = 0;
	hasxyinfo = 0;
	txtpos++;						// step past open parens
	x = expression();				// get value of X dimension
	if (expression_error)			// if bad index...
		return  0;					// 0 means bad expression
		
	if (*txtpos == ',')				// if found a comma separator...
	{
		hasxyinfo = 1;				// show this is 2D array info
		txtpos++;					// step past comma
		y=expression();				// get value of Y dimension
		if (expression_error)
			return  0;
	}

	if (*txtpos != ')')				// if badly formed array info...
		return  0;					// return error code

	txtpos++;						// leave txtpos pointing past closing parens
	offset = (ARRAY_X_SIZE * ARRAY_Y_SIZE) * (c - 'X');		// calc offset to base variable
	if (!hasxyinfo)					// if only has X dimension info...
	{
		offset = offset + x;
	}
	else 							// if has X and Y dimension info...
	{
		offset = offset + (x * ARRAY_X_SIZE) + y;		// add offset to requested cell
	}
	addr = addr + offset;
	
	return  addr;
}



static void			ShowProgramLockState(void)
{
	if (program_end == program_start)
	{
		printmsg(noprograminmemory);
		return;
	}
		
	if (lockrangestart == BEYOND_VALID_LINENUM)		// if unlocked...
	{
		printmsg(programunlocked);
	}
	else
	{
		printstr("Program is locked from line ");
		printnum(lockrangestart, RADIX_DECIMAL);
		printstr(" to ");
		if (lockrangeend == BEYOND_VALID_LINENUM)  printstr("end");
		else
		{
			printstr("line ");
			printnum(lockrangeend, RADIX_DECIMAL);
		}
		printstr(".\n");
	}
}


static int			AreYouSure(void)
{
	int				c;
	
	printmsg(AreYouSureMsg);
	while (1)
	{
		c = t_GetChar();
		t_OutChar(c);
		if ((c == 'y') || (c == 'Y'))
		{
			c = TRUE;
			break;
		}
		if ((c == 'n') || (c == 'N'))
		{
			c = FALSE;
			break;
		}
		t_OutChar('\b');
	}
	t_OutChar('\n');
	return  c;	
}




/*
 * Replacement for rand().  Rand() is not in most embedded libraries
 * and the web considers it garbage, anyway.
 * 
 * This code implements L'ecuyer's LFSR113 generator; code was taken
 * (with modifications) from:
 * https://stackoverflow.com/questions/1167253/implementation-of-rand
 * 
 * Modified 1 Oct 23 (KEL) to reseed the generator anytime the variable
 * MyRandomSeed changes value.  This allows seeding the generator, similar
 * to the behavior of srand() for traditional C RNG.  This also disconnects
 * all reliance on the traditional C RNG functions.  (WARNING! Not yet
 * tested thoroughly!)
 */
DATA_SIZE		MyRandom(void)
{
	DATA_SIZE				b;
	
	b  = ((z1 << 6) ^ z1) >> 13;
	z1 = ((z1 & 4294967294U) << 18) ^ b;
	b  = ((z2 << 2) ^ z2) >> 27; 
	z2 = ((z2 & 4294967288U) << 2) ^ b;
	b  = ((z3 << 13) ^ z3) >> 21;
	z3 = ((z3 & 4294967280U) << 7) ^ b;
	b  = ((z4 << 3) ^ z4) >> 12;
	z4 = ((z4 & 4294967168U) << 13) ^ b;
	return (z1 ^ z2 ^ z3 ^ z4) & DATA_SIZE_MAX;
};



/***************************************************************************/
static void ignore_blanks(void)
{
  while(*txtpos == SPACE || *txtpos == TAB)
    txtpos++;
}


#if 0
/***************************************************************************/
static void scantable(const unsigned char *table)
{
  int				i;
  
  i = 0;
  table_index = 0;
  
  while(1)
  {
    // Run out of table entries?
    if (*table == 0)
    {
		table_index = ENTRY_NOT_FOUND;
		return;
	}


    // Do we match this character?
    if ((txtpos[i] == *table) && (txtpos[i] != ' '))
    {
      i++;
      table++;
    }
    else
    {
      // if hit a space in the table, we have reached the end of the keyword
		if ((*table == ' ') && (i > 0))
      {
//		  printf("  i=%d  table_index=%d  ", i, table_index);					// debug
//        txtpos += i+1;  // Advance the pointer to following the keyword
        txtpos += i;  		// Advance the pointer to following the keyword	
        ignore_blanks();
        return;
      }

      // Forward to the end of this keyword
      while (*table != ' ')
        table++;

      // Now move on to the first character of the next word, and reset the position index
      table++;
      table_index++;
      ignore_blanks();
      i = 0;
    }
  }
}
#endif


/*
 * scantable      try to match chars in text buffer with entry in selected table
 * 
 * The original version of this routine did not need to support arbitrarily-
 * named ports, so any match in the table was good enough.  Since this version
 * of the core can support target ports such as ORANGE_LED, the scan needs to be
 * a bit more rigorous.  This means the scan won't return a match of the OR in
 * ORANGE_LED.
 * 
 * This implementation requires a space following any string to be found in the
 * table.  So:
 * 		100  A = C OR 5			 works
 * 		100  A = C OR5			 fails
 *
 */
static void scantable(const unsigned char *table)
{
  int				i;
  
	i = 0;								// index into text buffer
	table_index = 0;					// start at first entry in table
  
	//printstr("\nscantable: ");
	while (*table != 0)
	{
		//printnum(*table, RADIX_CHAR);
		// Do we match this character?
		if (txtpos[i] == *table)		// if char in buffer matches char in table...
		{
			if (*table == ' ')			// if we found the terminating space in table...
			{
				txtpos = txtpos + i;	// advance text position to space after keyword
				ignore_blanks();		// advance to next non-space char in buffer
				return;
			}
			i++;						// not done yet, move to next char in buffer
			table++;					// and next char in table
		}
		else if (*table == ' ')			// if hit end of keyword...
		{
			if ((txtpos[i] >= 'A' && txtpos[i] <= 'Z') || (txtpos[i] == '_'))
			{
				table++;					// move to first char in next entry (could be end!)
				table_index++;
				//ignore_blanks();
				i = 0;						// rewind the index into the text buffer
			}
			else 						// next char in buffer could be '(' or NL or ':'
			{
				txtpos = txtpos + i;	// advance text position to space after keyword
				ignore_blanks();		// advance to next non-space char in buffer
				return;
			}
		}
		else 							// chars don't match...
		{
			//printstr("|");
			while (*table != ' ')		// move to space after current keyword in table
				table++;
			table++;					// move to first char in next entry (could be end!)
			table_index++;
			//ignore_blanks();
			i = 0;						// rewind the index into the text buffer
		}
	}
	//printstr(" notfound\n");
	table_index = ENTRY_NOT_FOUND;		// nope, show the bad news
}


/***************************************************************************/
/*
 * pushb      push char in argument b onto character stack
 * 
 * Some bounds-checking would be nice...
 */
static void			pushb(unsigned char b)
{
	stackptr--;
	*stackptr = b;
}

/*
 * popb      pull character from character stack, return as char
 * 
 * Some bounds-checking would be nice...
 */
static unsigned char			popb()
{
	unsigned char				b;
	
	b = *stackptr;
	stackptr++;
	return  b;
}

/***************************************************************************/
void printnum(DATA_SIZE  num, int  radix)
{
  int			digits;
  char			c;
  
  if ((radix != RADIX_DECIMAL) && (radix != RADIX_HEX) && (radix != RADIX_CHAR))	// if not a legal radix...
		radix = RADIX_DECIMAL;						// should throw an error, maybe??
		
	if (radix == RADIX_CHAR)						// if printing a single ASCII char...
	{
		outchar((int)num & 0xff);
		return;
	}
  
	digits = 0;
  
	if (radix == RADIX_DECIMAL)
	{
		if (num < 0)
		{
			num = -num;
			outchar('-');
		}
		do
		{
			c = num % radix;
			num = num / radix;
			pushb(c+'0');
			digits++;
		}  while (num != 0);
	}
	
	if (radix == RADIX_HEX)
	{
		for (int n=0; n<sizeof(DATA_SIZE)*2; n++)
		{
			c = num & 0x0f;
			if (c > 9)  c = c + 7;
			num = num >> 4;
			pushb(c+'0');
			digits++;
			if (num == 0)  break;
		}	
	}

	while (digits > 0)
	{
		outchar(popb());
		digits--;
	}
}


void printUnum(UDATA_SIZE  num)
{
  int			digits;
  
  digits = 0;
  do {
    pushb(num%10+'0');
    num = num/10;
    digits++;
  }
  while (num > 0);

  while(digits > 0)
  {
    outchar(popb());
    digits--;
  }
}

/***************************************************************************/
static DATA_SIZE		testnum(void)
{
  DATA_SIZE				num;
  int					radix;
  int					c;
  
  num = 0;
  radix = 10;
  
  ignore_blanks();

	if ((txtpos[0] == '0') && (txtpos[1] == 'X'))
	{
		radix = 16;
		txtpos++;
		txtpos++;
	}
	
	if (radix == 10)
	{
		//while (isdigit((int)*txtpos))
		while (__isdigit((int)*txtpos))
		{
    // Trap overflows
			if (num >= (DATA_SIZE_MAX/10))
			{
				num = DATA_SIZE_MAX;
				break;
		}

		num = num *10 + *txtpos - '0';
		txtpos++;
	}
	
	if (radix == 16)
	{
		//while (isxdigit((int) *txtpos))
		while (__isxdigit((int) *txtpos))
		{
			if (num >= (DATA_SIZE_MAX/10))
			{
				num = DATA_SIZE_MAX;
				break;
			}
			c = *txtpos;
			c = c - '0';
			if (c > 9)  c = c - 7;

			num = num *16 + c;
			txtpos++;
		}
	}
  }
  return	num;
}

/***************************************************************************/
static unsigned char		print_quoted_string(void)
{
  int i=0;
  unsigned char			delim;
  
// txtpos now points to starting string delimiter (must be double-quote)
	delim = *txtpos;
	
//  if (delim != '"' && delim != '\'')		
  if (delim != DQUOTE)		// only double-quote recognized as string delimiter
    return 0;
  txtpos++;

  // Check we have a closing delimiter
  while(txtpos[i] != delim)
  {
    if(txtpos[i] == NL)
      return 0;
    i++;
  }

  // Print the characters
  while(*txtpos != delim)
  {
	if (*txtpos == '\\')		// if this is the C escape char...
	{
		txtpos++;				// find out what we are escaping
		switch  (*txtpos)
		{
			case  'r':			// return char
			outchar('\r');
			break;
		  
			case  'n':			// newline char
			outchar('\n');
			break;
		  
			case  '\\':			// \ char
			outchar('\\');
			break;
		  
			case  't':			// tab
			outchar('\t');
			break;
		  
			default:				// got me scratching, print a \ and this char
			outchar('\\');
			outchar(*txtpos);
			break;
			}
		}
	else
			outchar(*txtpos);
    txtpos++;
  }
  txtpos++; // Skip over the last delimiter

  return 1;
}


/*
 * printmsg      print text string stored as const
 */
void     printmsg(const unsigned char *msg)
{
  while (*msg != 0 )
  {
    outchar(*msg++);
  };
}


/*
 * printstr      print text string stored in RAM or as an argument
 */
void		printstr(char  *str)
{
	while (*str != 0)
	{
		outchar(*str++);
	}
}
 
 
void  printnl(void)
{
	outchar('\n');
}


/*
 * printUntilNL      print text until hit NL char or null
 * 
 * Primarily used in debugging, to display the current text buffer or a part
 * of an input line.
 */
void		printUntilNL(unsigned char  *msg)
{
	while (*msg != 0 && *msg != NL)
	{
		outchar(*msg++);
	}
}


/***************************************************************************/
static void getln(char prompt)
{
	unsigned char			*txtstart;
	char					c;
	
	txtstart = program_end+sizeof(LINENUM);
  outchar(prompt);
  txtpos = txtstart;

  while(1)
  {
    c = inchar();
    switch(c)
    {
    case NL:
      //break;
    case CR:
		printnl();
      // Terminate all strings with a NL
      txtpos[0] = NL;
      return;
    case CTRLH:				// backspace
      if (txtpos != txtstart)
      {
			txtpos--;
			outchar('\b');
			outchar(' ');
			outchar('\b');
		}
      break;
    default:
      // We need to leave at least one space to allow us to shuffle the line into order
      if(txtpos == variables_begin-2)
        outchar(BELL);
      else
      {
		*txtpos = c;				// sorry, the [0] looks weird...  KEL
//        txtpos[0] = c;
        txtpos++;
        outchar(c);
      }
    }
  }
}

/***************************************************************************/
static unsigned char *findline(void)
{
  unsigned char *line = program_start;
  while(1)
  {
    if(line == program_end)
      return line;

    if(((LINENUM *)line)[0] >= linenum)
      return line;

    // Add the line length onto the current address, to get to the next line;
    line += line[sizeof(LINENUM)];
  }
}

/***************************************************************************/
static void toUppercaseBuffer(void)
{
  unsigned char *c = program_end+sizeof(LINENUM);
  unsigned char quote = 0;

  while(*c != NL)
  {
    // Are we in a quoted string or comment line?
    if (*c == quote)
      quote = 0;
    else if (*c == '"' || *c == '\'')
      quote = *c;
    else if (*c == '\\')
		quote = 1;
    else if(quote == 0 && *c >= 'a' && *c <= 'z')
      *c = *c + 'A' - 'a';
    c++;
  }
}

/***************************************************************************/
void printline()
{
  LINENUM line_num;

  line_num = *((LINENUM *)(list_line));
  list_line += sizeof(LINENUM) + sizeof(char);

  // Output the line */
  printnum(line_num, RADIX_DECIMAL);
  outchar(' ');
  while(*list_line != NL)
  {
    outchar(*list_line);
    list_line++;
  }
  list_line++;
  printnl();
}

/***************************************************************************/
static DATA_SIZE  expr4(void)
{
	unsigned char				f;
	DATA_SIZE					*a;
	DATA_SIZE					v;
	DATA_SIZE					r1;
	DATA_SIZE					r2;
	int							c;
	unsigned char				*savetxtpos;
	DATA_SIZE					result;
	LINENUM						t;
	
  // fix provided by Jurg Wullschleger wullschleger@gmail.com
  // fixes whitespace and unary operations

	ignore_blanks();
	result = 0;						// default return value

	if( *txtpos == '-' )
	{
		txtpos++;
		result = -expr4();
		goto  expr4_exit;
	}
	// end fix
  
/*
 * check for unary logical negation (NOT)
 */
	savetxtpos = txtpos;
	scantable(logicop_tab);
	if (table_index == LOGICOP_NOT)
	{
		v = expr4();
		if (v)  result = 0;		//return  FALSE;
		else    result = 1;		//return  TRUE;
		goto expr4_exit;
	}
	txtpos = savetxtpos;

/*
 * if next two chars are "0X", collect a hex integer from text buffer
 */
	if ((txtpos[0] == '0') && (txtpos[1] == 'X'))
	{
		txtpos++;
		txtpos++;
		v = 0;
		while  (1)
		{
			c = *txtpos;
			//if (!isxdigit(c))  break;
			if (!__isxdigit(c))  break;
			c = c - '0'; 
			if (c > 9) c = c - 7;
			v = v * 16 + c;
			txtpos++;
		};
		result = v;
		goto expr4_exit;
	}


	if (*txtpos == '0')
	{
		txtpos++;
		result = 0;
		goto expr4_exit;
	}

/*
 * if char is a non-zero decimal digit, collect an integer from text buffer
 */
	if(*txtpos >= '1' && *txtpos <= '9')
	{
		v = 0;
		do
		{
			v = v*10 + *txtpos - '0';
			txtpos++;
		}  while(*txtpos >= '0' && *txtpos <= '9');
		result = v;
		goto expr4_exit;
	}

/*
 * if char is single-quote, process 'c' or '\x' and read ASCII value
 */
	if (*txtpos == SQUOTE)
	{
		if (txtpos[2] == SQUOTE)
		{
			v = txtpos[1];
			txtpos = txtpos + 3;
			result = v;
			goto expr4_exit;
		}
		
		if ((txtpos[3] == SQUOTE) && (txtpos[1] == '\\'))
		{
			v = txtpos[2];
			if      (v == 't')  v = TAB;
			else if (v == 'n')  v = NL;
			else if (v == 'r')  v = CR;
			else if (v == '0')  v = 0;
			else  ;						// this handles special case of '\\'
			txtpos = txtpos + 4;
			result = v;
			goto expr4_exit;
		}
		expression_error = E_BAD_CHAR_CONSTANT_SQUOTE;
		goto expr4_exit;
	}

/*
 * if the char is CHAR_CURRENT_LINENUM, return current line number
 */
	if (*txtpos == '$')
	{
		t = *((LINENUM *)(current_line));
		result = (DATA_SIZE)t;
		txtpos = txtpos + 1;
		goto expr4_exit;
	}

	// Is it a function, port, or variable reference?
	if (txtpos[0] >= 'A' && txtpos[0] <= 'Z')
	{
		// Is it a variable reference (single alpha)?
		if (txtpos[1] < 'A' || txtpos[1] > 'Z')
		{
			a = CalcAddressOfVariable();
			v = *a;
			result = v;
			goto expr4_exit;
		}

		// is it an I/O port?
		scantable(ports_tab);
		if (table_index != ENTRY_NOT_FOUND)				// if found the port
		{
			v = t_ReadPort(table_index);
			result = v;
			goto expr4_exit;
		}
	
		// Is it a function with a single parameter
		scantable(func_tab);
		if (table_index == ENTRY_NOT_FOUND)
		{
			expression_error = E_UNKNOWN_VAR_PORT_FUNC;
			goto expr4_exit;
		}

		f = table_index;

		if (*txtpos != '(')
		{
			expression_error = E_MISSING_OPEN_PAREN;
				goto expr4_exit;
		}

		txtpos++;
    
/*
 * This class of functions expects a single argument (either variable or array element).
 */
		if (f == FUNC_ADDR)
		{
			ignore_blanks();
			if ((*txtpos >= 'A') && (*txtpos <= 'Z'))
			{
				a = CalcAddressOfVariable();
				if (*txtpos != ')')
				{
					expression_error = E_MISSING_CLOSING_PAREN;
					goto expr4_exit;
				}
				txtpos++;
				result = (DATA_SIZE)a;
				goto expr4_exit;
			}
			expression_error = E_ADDR_FUNC_REQUIRES_VAR_ARG;
			goto expr4_exit;
		}
	
		if (f == FUNC_TONEQ)
		{
			ignore_blanks();
			if (*txtpos != ')')
			{
				expression_error = E_MISSING_CLOSING_PAREN;
				goto expr4_exit;
			}
		
			txtpos++;
			result = t_CheckToneStatus();
			goto expr4_exit;
		}
	
/*
 * Not ADDR() or TONE?() function, assume another function.  Get the expression between the
 * parentheses into variable v.
 */			
		v = expression();
		if (*txtpos != ')')
		{
			expression_error = E_MISSING_CLOSING_PAREN;
			goto expr4_exit;
		}
		txtpos++;
    
		switch (f)
		{
			case FUNC_PEEK:
			return t_program[v];				// why is this limited to the program space?  fix this...
      
			case FUNC_ABS:
			if (v < 0)  result = -v;
			else  		result = v;
			goto expr4_exit;

			case FUNC_RND:
			if (v == 0)
			{
				expression_error = E_ZERO_ARG_FOR_RAND;
				goto expr4_exit;
			}
			r1 = MyRandom();
			r2 = r1 / v;
			result = r1 - (r2 * v);
			goto expr4_exit;
		}
	}

	if (*txtpos == '(')
	{
		txtpos++;
		result = expression();
		if (*txtpos != ')')
		{
			expression_error = E_MISSING_CLOSING_PAREN;
			goto expr4_exit;
		}

		txtpos++;
		goto expr4_exit;
	}
  
/*
 * At this point, no clue what the user entered.  Need to throw an error and let someone else
 * deal with it.
 */
	expression_error = E_UNKNOWN_CHAR_OR_OPERATOR;
	
	expr4_exit:
	return  result;
}


/*
 * expr3a      process shift operators
 */
 static DATA_SIZE expr3a(void)
 {
	DATA_SIZE			result;
	DATA_SIZE			b;
	 
	result = expr4();
	ignore_blanks();
	
	if (expression_error)  goto expr3a_exit;     //return  a;
	
	scantable(shiftop_tab);
	if (table_index == ENTRY_NOT_FOUND)  goto expr3a_exit;   //return  a;
	 
	if (table_index == SHIFT_RIGHT) 		// right-shift
	{
		ignore_blanks();
		b = expr4();
		result = result >> b;
	}
	
	if (table_index == SHIFT_LEFT)	 		// left-shift
	{
		ignore_blanks();
		b = expr4();
		result = result << b;
	}
	
expr3a_exit:	
	return  result;			//return a;
}



/*
 *  expr3      process multiply/divide
 */
static DATA_SIZE  expr3(void)
{
  DATA_SIZE				result;
  DATA_SIZE				b;

	result = expr3a();

	ignore_blanks(); // fix for eg:  100 a = a + 1
	while (1)
	{
		if (*txtpos == '*')
		{
			txtpos++;
			b = expr3a();
			result = result * b;
		}
		else if (*txtpos == '/')
		{
			txtpos++;
			b = expr3a();
			if (b != 0)
				result = result / b;
			else
			{
				expression_error = E_DIVIDE_BY_ZERO;
				goto expr3_exit;
			}
		}
		else
			break;
	}
expr3_exit:
		return  result;
}



/*
 * expr2a      process % operator (modulus)
 * 
 * This routine supports both % (C-style) and MOD (traditional BASIC)
 * operators.
 */
 static DATA_SIZE	expr2a(void)
 {
	DATA_SIZE			result;
	DATA_SIZE			b;

	result = expr3();
	
	while (1)
	{
		if (*txtpos == '%')				// if processing % modulus operator...
		{
			txtpos++;
		}
		else if ((txtpos[0] == 'M') && (txtpos[1] == 'O') && (txtpos[2] == 'D'))  // if processing MOD modulus operator...
		{
			txtpos = txtpos + 3;
		}
		else 							// not modulus, try something else
		{
			break;
		}
	
		b = expr3();					// get 2nd value
		if (b == 0)
		{
			expression_error = E_DIVIDE_BY_ZERO;
			goto expr2a_exit;
		}
		result = result % b;
	}
	
expr2a_exit:	
	return  result;
}



/*
 * expr2      process addition/subtraction
 */
static DATA_SIZE	 expr2(void)
{
  DATA_SIZE			result;
  DATA_SIZE			b;

  if(*txtpos == '-' || *txtpos == '+')
    result = 0;
  else
    result = expr2a();

  while (1)
  {
    if (*txtpos == '-')
    {
      txtpos++;
      b = expr2a();
      result = result - b;			//a -= b;
    }
    else if(*txtpos == '+')
    {
      txtpos++;
      b = expr2a();
      result = result + b;
    }
    else
		break;
  }
  
	return  result;
}



/*
 * expr1      process logical operators
 */
 static DATA_SIZE expr1(void)
 {
	DATA_SIZE			result;
	DATA_SIZE			b;
	 
	result = expr2();
	if (expression_error)  goto expr1_exit;  //return  a;
	 
	scantable(logicop_tab);
	switch  (table_index)
	{
		case  LOGICOP_AND:
		b = expr2();
		result = result & b;
		break;
		
		case  LOGICOP_OR:
		b = expr2();
		result = result | b;
		break;
		
		case  LOGICOP_XOR:
		b = expr2();
		result = result ^ b;
		break;
		
		case  ENTRY_NOT_FOUND:
		break;
		
		/*
		 * LOGICOP_NOT is handled in expr4 as unary logical negation
		 */
	}
expr1_exit:
	return  result;
}
	 
	 
/***************************************************************************/
static DATA_SIZE  expression(void)
{
  DATA_SIZE				b;
  DATA_SIZE				result;

	result = expr1();			// get first value (may be only value!)

  // Check if we have an error
	if (expression_error)  goto  expression_exit;  //	return a;

	// see if next token is a relational operator
	scantable(relop_tab);
	if (table_index == ENTRY_NOT_FOUND)		// if not a relational operator...
		goto  expression_exit;			// only have one value, return result  //return a;

	switch (table_index)
	{
		case RELOP_GE:
		b = expr1();
		if (result >= b) result = 1;
		else 			 result = 0;
		break;

		case RELOP_NE:
		case RELOP_NE_BANG:
		b = expr1();
		if (result != b) result = 1;
		else 			 result = 0;
		break;
		
		case RELOP_GT:
		b = expr1();
		if (result > b) result = 1;
		else 			result = 0;
		break;
		
		case RELOP_EQ:
		b = expr1();
		if (result == b) result = 1;
		else 			 result = 0;
		break;
		
		case RELOP_LE:
		b = expr1();
		if (result <= b) result = 1;
		else 			 result = 0;
		break;
		
		case RELOP_LT:
		b = expr1();
		if (result < b) result = 1;
		else 			result = 0;
		break;
	}
  
expression_exit:
	return  result;
}




/***************************************************************************/
void loop()
{
  unsigned char 		*start;
  unsigned char 		*newEnd;
  unsigned char 		linelen;
  DATA_SIZE				*addr;
  boolean				suppressNL;
  int					radix;				// used by print and printx
  int					csave;
  LINENUM				line_num;			// used on break

  

	program_start = t_program;
	program_end = program_start;
	stackptr = t_program+sizeof(t_program);  		// Needed for printnum
	stack_limit = stackptr - STACK_SIZE;
	variables_begin = stack_limit - TOTAL_VARIABLE_SPACE;

  // memory free
  printnum(variables_begin-program_end, RADIX_DECIMAL);
  printmsg(memorymsg);

warmstart:
  // current_line at 0 means interpreter is running in 'direct' mode.
  current_line = 0;
  stackptr = t_program + sizeof(t_program);
  
  printmsg(okmsg);

prompt:
  if (triggerRun )
  {
    triggerRun = FALSE;
    current_line = program_start;
    goto execline;
  }

  getln( '>' );
  toUppercaseBuffer();

  txtpos = program_end+sizeof(unsigned short);
	if (*txtpos == '\0')  goto prompt;
	
  // Find the end of the freshly entered line
  while (*txtpos != NL)
    txtpos++;

  // Move it to the end of program_memory
  {
    unsigned char *dest;
    dest = variables_begin-1;
    while(1)
    {
      *dest = *txtpos;
      if(txtpos == program_end+sizeof(unsigned short))
        break;
      dest--;
      txtpos--;
    }
    txtpos = dest;
  }

  // Now see if we have a line number
  linenum = (uint16_t)testnum();
  
  ignore_blanks();
  if (linenum == 0)
    goto direct;

  if (linenum == BEYOND_VALID_LINENUM)
    goto qhow;

  // Find the length of what is left, including the (yet-to-be-populated) line header
  linelen = 0;
  while(txtpos[linelen] != NL)
    linelen++;
  linelen++; // Include the NL in the line length
  linelen += sizeof(unsigned short)+sizeof(char); // Add space for the line number and line length

  // Now we have the number, add the line header.
  txtpos -= 3;


  *((unsigned short *)txtpos) = linenum;
  txtpos[sizeof(LINENUM)] = linelen;


/*
 * Test new line number against lock range.  If line number is within lock
 * range, cannot modify or delete this line.
 */
	if (linenum >= lockrangestart && linenum <= lockrangeend)
	{
		//ShowProgramLockState();
		goto qhow;
	}

  // Merge it into the rest of the program
  start = findline();

  // If a line with that number exists, then remove it
  if(start != program_end && *((LINENUM *)start) == linenum)
  {
    unsigned char *dest, *from;
    unsigned tomove;

    from = start + start[sizeof(LINENUM)];
    dest = start;

    tomove = program_end - from;
    while( tomove > 0)
    {
      *dest = *from;
      from++;
      dest++;
      tomove--;
    }	
    program_end = dest;
  }

  if(txtpos[sizeof(LINENUM)+sizeof(char)] == NL) // If the line has no txt, it was just a delete
    goto prompt;



  // Make room for the new line, either all in one hit or lots of little shuffles
  while(linelen > 0)
  {	
    unsigned int tomove;
    unsigned char *from,*dest;
    unsigned int space_to_make;

    space_to_make = txtpos - program_end;

    if(space_to_make > linelen)
      space_to_make = linelen;
    newEnd = program_end + space_to_make;
    tomove = program_end - start;


    // Source and destination - as these areas may overlap we need to move bottom up
    from = program_end;
    dest = newEnd;
    while(tomove > 0)
    {
      from--;
      dest--;
      *dest = *from;
      tomove--;
    }

    // Copy over the bytes into the new space
    for(tomove = 0; tomove < space_to_make; tomove++)
    {
      *start = *txtpos;
      txtpos++;
      start++;
      linelen--;
    }
    program_end = newEnd;
  }
  goto prompt;

unimplemented:
  printmsg(unimplimentedmsg);
  goto prompt;

qhow:
	{
		LINENUM			t;
		
		printmsg(howmsg);
		if (current_line != NULL)
		{
			t = *((LINENUM *)(current_line));
			printstr(" (line ");
			printnum(t, RADIX_DECIMAL);
			printstr(")");
		}
		printnl();
		goto prompt;
	}

qwhat:
	{
		printmsg(whatmsg);
		if (current_line != NULL)
		{
			unsigned char tmp = *txtpos;
		
			if(*txtpos != NL)
				*txtpos = '^';
			list_line = current_line;
			printline();
			*txtpos = tmp;
		}
		printnl();
		goto prompt;
	}

qsorry:
	{	
		LINENUM			t;
		
		printmsg(sorrymsg);
		if (current_line != NULL)
		{
			t = *((LINENUM *)(current_line));
			printstr(" (line ");
			printnum(t, RADIX_DECIMAL);
			printstr(")");
		}
		printnl();
		goto warmstart;
	}

run_next_statement:
	ignore_blanks();
	if (*txtpos == MIDEOL)			// was while; that didn't look right...
	{
		txtpos++;
		ignore_blanks();
	}
	if (*txtpos == NL)
		goto execnextline;
  
	goto interperateAtTxtpos;

direct: 
  txtpos = program_end + sizeof(LINENUM);
  if(*txtpos == NL)
    goto prompt;

interperateAtTxtpos:
  if(breakcheck())
  {
		inhibitOutput = FALSE;
		t_SetTone(0,0);					// shut off tone generation, if any
		line_num = *((LINENUM *)(current_line));
		printmsg(breakmsg);
		printnum(line_num, RADIX_DECIMAL);
		printstr("!\n");
		goto warmstart;
  }

	scantable(keywords);
	switch(table_index)
	{
		case KW_FILES:
		goto files;
    
		case  KW_DELETE:
		goto  delete;
	
		case KW_LIST:
		goto list;

		case KW_CHAIN:
		goto chain;

		case KW_LOAD:
		goto load;

		case  KW_MERGE:
		goto merge;
	
		case KW_MEM:
		goto mem;

		case KW_NEW:
		if (txtpos[0] != NL)
			goto qwhat;
		if (program_start != program_end)			// if program in memory...
		{
			printmsg(EraseWarning);
			csave = AreYouSure();
			if (csave)
			{
				program_end = program_start;
				lockrangeend = BEYOND_VALID_LINENUM;		// always remove lock on new
				lockrangestart = BEYOND_VALID_LINENUM;		// always remove lock on new
			}
		}
		goto prompt;
	
		case KW_RUN:
		current_line = program_start;
		goto execline;
    
		case KW_SAVE:
		goto save;
    
		case KW_FLSAVE:
		goto flsave;

		case KW_NEXT:
		goto next;
    
		case KW_LET:
		goto assignment;
    
		case KW_IF:
		{
			short int val;
		
			expression_error = 0;
			val = expression();

			if (expression_error || *txtpos == NL)
				goto qhow;
			if (val != 0)
			{
				goto interperateAtTxtpos;
			}
			goto execnextline;
		}

		case KW_GOTO:
		expression_error = 0;
		linenum = expression();
		if (expression_error || *txtpos != NL)
			goto qhow;
		current_line = findline();
		goto execline;

		case KW_GOSUB:
		goto gosub;

		case KW_RETURN:
		goto gosub_return; 

		case KW_REM:
		case KW_QUOTE:
		goto execnextline;	// Ignore line completely

		case KW_FOR:
		goto forloop; 

		case KW_INPUT:
		goto input;
     
		case KW_PRINT:
		case KW_QMARK:
		goto print;
    
		case KW_PRINTX:
		case KW_QMARKX:
		goto printx;

		case  KW_PRINTA:
		case  KW_QMARKA:
		goto  printa;
	
		case KW_POKE:
		goto poke;
    
		case KW_END:
		case KW_STOP:
    // This is the easy way to end - set the current line to the end of program attempt to run it
		if (txtpos[0] != NL)
			goto qwhat;
		current_line = program_end;
		goto execline;
  
		case KW_BYE:    // Leave the basic interperater
		if (current_line > 0)			// do not execute BYE from inside a program!
		{
			printstr("\nCannot execute BYE from inside a program!\n");
			goto qsorry;
		}
		if (program_start != program_end)			// if program in memory...
		{
			printmsg(EraseWarning);
			csave = AreYouSure();
			if (!csave)					// if operator says "no"...
			{
				goto execnextline;
			}
		}
		forcereboot = FALSE;
		return;

		
		case KW_REBOOT:	// leave the basic interpreter and force hardware reset afterwards
		if (current_line > 0)			// do not allow reset from inside a program!
		{
			printstr("\nCannot force a reboot from inside a program!\n");
			goto qsorry;
		}
		if (program_start != program_end)			// if program in memory...
		{
			printmsg(EraseWarning);
			csave = AreYouSure();
			if (!csave)					// if operator says "no"...
			{
				goto execnextline;
			}
		}
		forcereboot = TRUE;
		return;

	
		case KW_AWRITE:  // AWRITE <pin>, HIGH|LOW
		//isDigital = FALSE;
		goto awrite;

		case KW_DWRITE:  // DWRITE <pin>, HIGH|LOW
		//isDigital = TRUE;
		goto dwrite;

		case KW_RSEED:
		goto rseed;

		case KW_WORDS:
		goto words;
	
		case KW_TIMERRATE:
		goto timerrate;
	
		case KW_ADDTIMER:
		goto addtimer;
	
		case KW_DELTIMER:
		goto deltimer;
	
		case KW_TONE:
		goto tone;
	
		case KW_BEEP:
		goto beep;
	
		case  KW_LOCKQ:
		goto lockq;

		case KW_LOCK:
		goto lock;
	
		case KW_UNLOCK:
		goto unlock;
	
		case KW_OUTCHAR:
		goto kwoutchar;
	
		case KW_TEST:
		goto test;
		
		case ENTRY_NOT_FOUND:			// if no entry in table for this token, try assignment
		goto assignment;
    
		default:
		break;
  }

execnextline:
  if(current_line == NULL)		// Processing direct commands?
    goto prompt;
  current_line +=	 current_line[sizeof(LINENUM)];

execline:
  if(current_line == program_end) // Out of lines to run
    goto warmstart;
  txtpos = current_line+sizeof(LINENUM)+sizeof(char);
  goto interperateAtTxtpos;


/*
input:
  {
    unsigned char 	var;
    DATA_SIZE		value;
    
    ignore_blanks();
    if(*txtpos < 'A' || *txtpos > 'Z')
      goto qwhat;
    var = *txtpos;
    txtpos++;
    ignore_blanks();
    if(*txtpos != NL && *txtpos != MIDEOL)
      goto qwhat;
inputagain:
    tmptxtpos = txtpos;
    getln( '?' );
    toUppercaseBuffer();
    txtpos = program_end+sizeof(unsigned short);
    ignore_blanks();
    expression_error = 0;
    value = expression();
    if (expression_error)
      goto inputagain;
      
    //((short int *)variables_begin)[var-'A'] = value;
    addr = CalcAddressOfVariable(var);
    *addr = value;
    txtpos = tmptxtpos;

    goto run_next_statement;
  }
*/


input:
  {
	int				nvars;
	int				n;
	DATA_SIZE		value;
	struct  var_name_addr		vars[20];		// magic number! max number of vars in INPUT line
	
/*
 * Collect all the variable names and addresses from the INPUT statement
 */
    nvars = 0;
    do
    {
		ignore_blanks();
		if(*txtpos < 'A' || *txtpos > 'Z')
			goto qwhat;
		if (nvars == sizeof(vars))
			goto qsorry;
		
		vars[nvars].basename = *txtpos;		// save base variable name
		addr = CalcAddressOfVariable();		// now have address of n'th variable
		vars[nvars].addr = addr;			// save address of variable
		nvars++;
		ignore_blanks();
		if (*txtpos == ',')  txtpos++;
	}
	while (*txtpos != NL && *txtpos != MIDEOL);
	if (nvars == 0)				// if no variables in INPUT statement...
		goto qwhat;
	
	tmptxtpos = txtpos;			// record end of INPUT statement

	n = 0;						// start with first variable in vars[] list
	while (n < nvars)
	{
inputagain:
		outchar(vars[n].basename);
		outchar(' ');
		outchar('?');
		getln(' ');
		toUppercaseBuffer();
		txtpos = program_end + sizeof(unsigned short);
		while (*txtpos != NL)
		{
			ignore_blanks();
			expression_error = 0;
			value = expression();		// now have first value in newly entered input
			if (expression_error)
				goto inputagain;
			*vars[n].addr = value;
			n++;
			ignore_blanks();
			if (*txtpos == ',')
			{
				txtpos++;
				ignore_blanks();
			}
		}
		if (n == nvars)  break;
	}
    txtpos = tmptxtpos;					// done with input buffer, return to program
	goto run_next_statement;
}

		
/*
 * FOR loop
 * This code iterates through a FOR loop.  Note that the iterator MUST
 * be a simple variable, not an array element!  All array info will be
 * ignored; for variables X, Y, and Z, the base variable will be used.
 */
forloop:
  {
    unsigned char		var;
    DATA_SIZE			initial;
    DATA_SIZE			step;
    DATA_SIZE			terminal;
    
    ignore_blanks();
    if(*txtpos < 'A' || *txtpos > 'Z')
      goto qwhat;
    
	if (txtpos[1] == '(')				// cannot use an array element as a FOR iterator!
		goto qsorry;
		
    var = *txtpos;
    addr = CalcAddressOfVariable();		// this will give address of base variable
    //txtpos++;
    ignore_blanks();
    if(*txtpos != '=')
      goto qwhat;
    txtpos++;
    ignore_blanks();

    expression_error = 0;
    initial = expression();
    if(expression_error)
      goto qwhat;

    scantable(to_tab);
    if(table_index != 0)
      goto qwhat;

    terminal = expression();
    if(expression_error)
      goto qwhat;

    scantable(step_tab);
    if(table_index == 0)
    {
      step = expression();
      if(expression_error)
        goto qwhat;
    }
    else
      step = 1;
    ignore_blanks();
    if(*txtpos != NL && *txtpos != MIDEOL)
      goto qwhat;


    if(!expression_error && *txtpos == NL)
    {
      struct stack_for_frame *f;
      if(stackptr + sizeof(struct stack_for_frame) < stack_limit)
        goto qsorry;

      stackptr -= sizeof(struct stack_for_frame);
      f = (struct stack_for_frame *)stackptr;
      //((DATA_SIZE *)variables_begin)[var-'A'] = initial;
      //addr = CalcAddressOfVariable(var, 0, 0);
      *addr = initial;
      f->frame_type = STACK_FOR_FLAG;
      f->for_var = var;
      f->terminal = terminal;
      f->step     = step;
      f->txtpos   = txtpos;
      f->current_line = current_line;
      goto run_next_statement;
    }
  }
  goto qhow;

gosub:
  expression_error = 0;
  linenum = expression();
  if(!expression_error && *txtpos == NL)
  {
    struct stack_gosub_frame *f;
    if(stackptr + sizeof(struct stack_gosub_frame) < stack_limit)
      goto qsorry;

    stackptr -= sizeof(struct stack_gosub_frame);
    f = (struct stack_gosub_frame *)stackptr;
    f->frame_type = STACK_GOSUB_FLAG;
    f->txtpos = txtpos;
    f->current_line = current_line;
    current_line = findline();
    goto execline;
  }
  goto qhow;

next:
  // Fnd the variable name
  ignore_blanks();
  if(*txtpos < 'A' || *txtpos > 'Z')
    goto qhow;
  txtpos++;
  ignore_blanks();
  if(*txtpos != MIDEOL && *txtpos != NL)
    goto qwhat;

gosub_return:
  // Now walk up the stack frames and find the frame we want, if present
  tempsp = stackptr;
  while (tempsp < t_program + sizeof(t_program)-1)
  {
    switch(tempsp[0])
    {
    case STACK_GOSUB_FLAG:
      if(table_index == KW_RETURN)
      {
        struct stack_gosub_frame *f = (struct stack_gosub_frame *)tempsp;
        current_line	= f->current_line;
        txtpos			= f->txtpos;
        stackptr += sizeof(struct stack_gosub_frame);
        goto run_next_statement;
      }
      // This is not the loop you are looking for... so Walk back up the stack
      tempsp += sizeof(struct stack_gosub_frame);
      break;
    case STACK_FOR_FLAG:
      // Flag, Var, Final, Step
      if(table_index == KW_NEXT)
      {
        struct stack_for_frame *f = (struct stack_for_frame *)tempsp;
        // Is the the variable we are looking for?
        if(txtpos[-1] == f->for_var)
        {
			csave = *txtpos;					// need to save char following base variable letter in buffer
			*txtpos = ' ';						// smudge any array info following base letter
			txtpos--;							// backup to base variable letter
          addr = CalcAddressOfVariable();		// this sets addr to address of base variable, even if array info was present
          *txtpos = csave;						// restore smudged char
          *addr = *addr + f->step;
          // Use a different test depending on the sign of the step increment
          if((f->step > 0 && *addr <= f->terminal) || (f->step < 0 && *addr >= f->terminal))
          {
            // We have to loop so don't pop the stack
            txtpos = f->txtpos;
            current_line = f->current_line;
            goto run_next_statement;
          }
          // We've run to the end of the loop. drop out of the loop, popping the stack
          stackptr = tempsp + sizeof(struct stack_for_frame);
          goto run_next_statement;
        }
      }
      // This is not the loop you are looking for... so Walk back up the stack
      tempsp += sizeof(struct stack_for_frame);
      break;
    default:
      //printf("Stack is stuffed!\n");
      goto warmstart;
    }
  }
  // Didn't find the variable we've been looking for
  goto qhow;

assignment:
  {
    DATA_SIZE		value;
    DATA_SIZE		*addr;
    int				index;
    unsigned char	varname;
    int				updateaddr;

    if(*txtpos < 'A' || *txtpos > 'Z')
      goto qhow;
    
/*
 * check if this is a write to a port
 */
	index = -1;					// assume we won't find the entry
	scantable(ports_tab);
	if (table_index != ENTRY_NOT_FOUND)
	{
		index = table_index;
	}
	else 				// not port, must be a variable
	{
		varname = *txtpos;				// record for later extended initialization
		addr = CalcAddressOfVariable();
		if (addr == 0)			// if that didn't work...
			goto qwhat;
	}
	
    ignore_blanks();

/*
 * Found the assignment target (either a port or a variable).  Now process
 * the value to write.
 */
    if (*txtpos != '=')
      goto qwhat;
    txtpos++;
    ignore_blanks();
    expression_error = 0;
    value = expression();
    if (expression_error)
      goto qwhat;
	
    if (index != -1)
		t_WritePort(index, value);
	else
	{
		*addr = value;
	
	/*
	 * Just initialized a single variable.  If we initialized X, Y, or Z,
	 * check for additional initialization of successive array elements.
	 * This mechanism overloads the assignment operator (=) for array
	 * elements.
	 * 
	 * Three variants are supported:
	 * 
	 * 		x = 1,2,3		\ inits X(0), X(1), and X(2)
	 * 		x(5) = 7,6,-1	\ inits X(5), X(6), and X(7)
	 * 		x(4,19) = 3,3,3	\ inits X(4,19), X(5,0), and X(5,1)
	 */
		ignore_blanks();
		while (*txtpos == ',')					// if need to init more elements...
		{
			if (varname != 'X' && varname != 'Y' && varname != 'Z')
				goto qwhat;
			
			txtpos++;						// move past comma
			ignore_blanks();
			updateaddr = TRUE;				// assume we will update the address
			if (*txtpos == ',')				// if no value, just ", ,", leave value unchanged
			{
				updateaddr = FALSE;			// show not to update this address
			}
			else
			{
				value = expression();
				if (expression_error)
					goto qwhat;
			}
			addr++;
			if (updateaddr)					// if we need to update the address...
				*addr = value;
			ignore_blanks();
		}
	}
		
    // Check that we are at the end of the statement
    if(*txtpos != NL && *txtpos != MIDEOL)
      goto qwhat;
    
  }
  goto run_next_statement;

poke:
  {
    DATA_SIZE			value;
    unsigned char 		*address;

    // Work out where to put it
    expression_error = 0;
    value = expression();
    if (expression_error)
      goto qwhat;
    address = (unsigned char *)value;

    // check for a comma
    ignore_blanks();
    if (*txtpos != ',')
      goto qwhat;
    txtpos++;
    ignore_blanks();

    // Now get the value to assign
    expression_error = 0;
    value = expression();
    if (expression_error)
      goto qwhat;
    //printf("Poke %p value %i\n",address, (unsigned char)value);
    // Check that we are at the end of the statement
    if(*txtpos != NL && *txtpos != MIDEOL)
      goto qwhat;
  }
  goto run_next_statement;

/*
 * LIST  [startline] [endline] 
 * 
 * Warning!  This code formed the basis of the SAVE code below.  If you change
 * the functionality of either LIST or SAVE, make those same changes in the other section.
 * (Actually, this needs to be factored into a function some day...)
 */
list:
{
	LINENUM			lineend;
	
	linenum = testnum();			// returns 0 if no line number found
	
	if (linenum)					// if user entered a starting line number...
	{
		if (*txtpos != NL)				// if not end of line, should be an ending line number
		{
			ignore_blanks();
			if (*txtpos == '-')			// '-' means "to end of program"
			{	
				lineend = BEYOND_VALID_LINENUM;		// see if there is an ending line number
				txtpos++;				// done with this char
			}
			else
			{
				lineend = testnum();		// see if user entered ending line in range to print
				if (lineend == 0)			// if not a valid line number...
					goto qwhat;
			}
		}
		else 						// user entered just one line number
		{
			lineend = linenum;		// print only one line
		}
	}
	else 							// no starting line number found, do whole program
	{
		lineend = BEYOND_VALID_LINENUM;
	}


	ignore_blanks();
	// Should be EOL
	if(txtpos[0] != NL)
		goto qwhat;
    
    if (linenum > lineend)		// silly check
		goto qwhat;
		

	// Find the line
	list_line = findline();
	while((list_line != program_end) && ((LINENUM)list_line[0]) <= lineend)
		printline();
	goto warmstart;
}

unlock:
{
	lockrangestart = BEYOND_VALID_LINENUM;  // unlock be setting start of lock range beyond valid line number
	lockrangeend = BEYOND_VALID_LINENUM;	// do both ends of range
	ShowProgramLockState();
	goto  run_next_statement;
}


lockq:
{
	ShowProgramLockState();
	goto run_next_statement;
}


/*
 * LOCK keyword      marks a block of line numbers as locked for editing;
 * 					 text in these lines cannot be edited until unlocked.
 * 
 * Supports the following variants:
 * LOCK					reports program lock state
 * LOCK  100			locks program from line 100 to end
 * LOCK  100,200		locks program from line 100 to line 200 inclusive
 * LOCK  ,200			locks program from start to line 200 inclusive
 */
lock:
{
	uint32_t			b;			// holds line number of start of lock region
	uint32_t			e;			// holds line number of end of lock region
	
	if (program_end == program_start)			// if no program in memory...
	{
		printmsg(noprograminmemory);
		goto run_next_statement;
	}
	
	ignore_blanks();
	b = 1;						// assume locking full program
	e = BEYOND_VALID_LINENUM;	// assume locking full program
	expression_error = S_OK;
		
	if (*txtpos >= '1' && *txtpos <= '9')		// if 'LOCK xxx' or 'LOCK xxx,'
	{
		b = expression();		// get beginning line number
		if (expression_error != S_OK)	// not OK is bad!
			goto qwhat;
	}
			
	ignore_blanks();
	if (*txtpos == ',')				// if 'LOCK  ,xxx'...
	{
		txtpos++;					// move past comma
		ignore_blanks();			// and spaces
		if (*txtpos >= '1' && *txtpos <= '9')		// next token must be a line number
		{
			e = expression();		// get ending line number
			if (expression_error)	// non-zero is bad!
				goto qwhat;
		}
		else if (*txtpos == NL)		// if 'LOCK xxx,'...
		{
		}
		else
		{
			goto qwhat;					// sorry, that didn't work
		}
	}
	lockrangestart = b;				// if got here, args are valid, update range
	lockrangeend = e;

	ShowProgramLockState();
	goto run_next_statement;
}


kwoutchar:
{
    DATA_SIZE			value;
    unsigned char 		*address;

    // Figure out what to send
    expression_error = 0;
    value = expression();
    if (expression_error)
      goto qwhat;
	outchar((unsigned char) value);
	goto run_next_statement;
}


print:
	radix = RADIX_DECIMAL;
	goto _print;

printx:
	radix = RADIX_HEX;
	goto _print;
	
printa:
	radix = RADIX_CHAR;				// marker for ASCII output
	goto _print;
	
_print:
  // If we have an empty list then just put out a NL
  if (*txtpos == MIDEOL)
  {
    printnl();
    txtpos++;
    goto run_next_statement;
  }
  if (*txtpos == NL)
  {
	  printnl();
	goto execnextline;
  }

	suppressNL = FALSE;
  while (1)
  {
    ignore_blanks();
    if (print_quoted_string())
    {
      ;
    }
//    else if(*txtpos == '"' || *txtpos == '\'')  //  removed; allow 'x' for char value
//      goto qwhat;
	else if(*txtpos == NL)
	{
		if (suppressNL == FALSE)  printnl();
		goto execnextline;
	}
	else if (*txtpos == MIDEOL)
	{
		if (suppressNL == FALSE)  printnl();
		break;
	}
    else
    {
		DATA_SIZE			e;
      
		expression_error = 0;
		e = expression();
		if (expression_error)
			goto qwhat;
        
   		printnum(e, radix);			// print data in hex or decimal or ASCII char (radix=99)
		suppressNL = FALSE;
    }

    // At this point we have three options, a comma or a new line
    if(*txtpos == ',')				// if next char is comma (field separator)...
    {
		suppressNL = TRUE;
		outchar(' ');				// make it pretty...
		txtpos++;					// Skip the comma and move onto the next
	}
    else if(*txtpos == ';')
    {
		suppressNL = TRUE;
      txtpos++; // This has to be the end of the print - no newline
    }
    else	;				// let the next call to expression() catch any errors...	KEL
  }
  goto run_next_statement;

mem:
  // memory free
  printnum(variables_begin-program_end, RADIX_DECIMAL);
  printmsg(memorymsg);
  goto run_next_statement;


  /*************************************************/

//pinmode: // PINMODE <pin>, I/O
awrite: // AWRITE <pin>,val
dwrite:
  goto unimplemented;

  /*************************************************/
files:
{
	char		*ptr;
	
	ptr = t_GetFirstFileName();
	while (ptr)
	{
		printstr(ptr);
		printstr("  ");
		ptr = t_GetNextFileName(ptr);
	}
	printstr("\n");
	goto  run_next_statement;
}
		

delete:
{
	int				s;
	
	if (! T_SUPPORTS_FILES)
		goto unimplemented;

	ignore_blanks();
// Should be start of filename (quoted string)
	if(txtpos[0] == NL)
		goto qwhat;
    
//  now find the filname to delete
    expression_error = filenameWord();
    if (expression_error != S_OK)
		goto qwhat;
//    filename = filenameWord();
//    if (expression_error)
//      goto qwhat;

    s = t_DeleteFile(tempfilename);
    if (s != S_OK)
		goto qsorry;
	
	goto  run_next_statement;
}

			

chain:
	goto unimplemented;
  //runAfterLoad = TRUE;


/*
 * SAVE  [startline] [endline]  "filename"  
 * 
 * Warning!  This code uses a copy-paste block of code from LIST: above.  If you change
 * the functionality of either LIST or SAVE, make those same changes in the other section.
 * (Actually, this needs to be factored into a function some day...)
 */
save:
{
	LINENUM			lineend;
	
	if (! T_SUPPORTS_FILES)
		goto unimplemented;
		
//  Following code was copied from LIST: above
//  find the range of lines to save
	linenum = testnum();			// returns 0 if no line number found
	
	if (linenum)					// if user entered a starting line number...
	{
		if (*txtpos != NL)				// if not end of line, should be an ending line number
		{
			ignore_blanks();
			if (*txtpos == '-')			// '-' means "to end of program"
			{	
				lineend = BEYOND_VALID_LINENUM;		// show saving the entire program
				txtpos++;				// done with this char
			}
			else
			{
				lineend = testnum();		// see if user entered ending line in range to print
				if (lineend == 0)			// if not a valid line number...
					goto qwhat;
			}
		}
		else 						// user entered just one line number
		{
			lineend = linenum;		// print only one line
		}
	}
	else 							// no starting line number found, do whole program
	{
		lineend = BEYOND_VALID_LINENUM;	// show saving the entire program
	}


    if (linenum > lineend)		// silly check
		goto qwhat;
		
	ignore_blanks();
// Should be start of filename (quoted string)
	if(txtpos[0] == NL)
		goto qwhat;
    
//  now find the filname to save to
    expression_error = filenameWord();
    if (expression_error != S_OK)
      goto qwhat;

	if (t_FileExistsQ(tempfilename))
	{
		printmsg(overwritesavedfilemsg);
		if (AreYouSure() == FALSE)  goto warmstart;
	}
	
    wfp = t_OpenFile(tempfilename, "w");
		
    if (wfp == NULL)					// if could not open file...
		goto qsorry;
		
    t_SetOutputStream(T_STREAM_FILE);
    
    ignore_blanks();
	// Find the line
	list_line = findline();
	while ((list_line != program_end) && ((LINENUM)list_line[0]) <= lineend)
		printline();

    // finished saving the requested lines; this is the end of the code copied from LIST
    // go back to standard output, close the file
    t_SetOutputStream(T_STREAM_SERIAL);

    t_CloseFile(wfp);
    wfp = NULL;
    goto warmstart;
}


flsave:					// force save of RAM disc to flash, if supported
	if (! T_SUPPORTS_FILES)
		goto unimplemented;
		
	t_ForceWriteToFlash();
	goto warmstart;
	
	
load:
merge:
	if (! T_SUPPORTS_FILES)
		goto unimplemented;
		
    expression_error = filenameWord();				// get filename to load
    if (expression_error != S_OK)					// if no/bad filename, bad
      goto qwhat;

	rfp = t_OpenFile(tempfilename, "r");		// ask target to open the file
	if (rfp == NULL)						// if cannot open file, that's an error
		goto qhow;
		
	if (table_index == KW_LOAD)				// if loading a program...
	{
		if (program_start != program_end)	// if a program is already in memory...
		{
			printmsg(EraseWarning);
			if (AreYouSure() == FALSE)  goto warmstart;
			program_end = program_start;			// erase existing program
		}
	}
	
	t_SetInputStream(T_STREAM_FILE);
    inhibitOutput = TRUE;
	goto warmstart;


rseed:
  {
    DATA_SIZE		value;					// why doesn't this use the value variable declared at top?  KEL

    //Get the pin number
    expression_error = 0;
    value = expression();
    if(expression_error)
      goto qwhat;

	if (value == 0)  value = INITIAL_RANDOM_SEED;
	
    //srand( value );
    z1 = value;							// replaces srand(); see MyRandom() function
    z2 = value;
    z3 = value;
    z4 = value;
    goto run_next_statement;
  }

words:
	{
		printmsg(keywordsmsg);
		printmsg(keywords);
		outchar('\n');
		
		printmsg(functionsmsg);
		printmsg(func_tab);
		outchar('\n');
		
		printmsg(relopsmsg);
		printmsg(relop_tab);
		outchar('\n');
		
		printmsg(logicopsmsg);
		printmsg(logicop_tab);
		outchar('\n');

		printmsg(shiftopsmsg);
		printmsg(shiftop_tab);
		outchar('\n');

		printmsg(portsmsg);
		printmsg(ports_tab);
		outchar('\n');

		goto run_next_statement;
	}

timerrate:
	{
		DATA_SIZE			value;

		expression_error = 0;
		value = expression();
		if (expression_error)
			goto qwhat;
		t_SetTimerRate(value);
		
		goto run_next_statement;
	}
	
addtimer:
	{
		DATA_SIZE			*a;

		if ((*txtpos >= 'A') && (*txtpos <= 'Z'))
		{
			a = CalcAddressOfVariable();
			t_AddTimer(a);
		}
		goto run_next_statement;
	}
	
deltimer:
	{
		DATA_SIZE			*a;

		if ((*txtpos >= 'A') && (*txtpos <= 'Z'))
		{
			a = CalcAddressOfVariable();
			t_DeleteTimer(a);
		}
		goto run_next_statement;
	}
	
tone:
	{
		DATA_SIZE			freq;
		DATA_SIZE			duration;
		
		if (T_NUM_TONE_CHS == 0)	// if no tone channels
			goto qsorry;
			
		expression_error = 0;		// first argument is frequency (Hz)
		freq = expression();
		if (expression_error)
			goto qwhat;

		ignore_blanks();			// check for a comma
		if (*txtpos != ',')
			goto qwhat;
		txtpos++;

		ignore_blanks();			// second argument is duration (msecs)
		duration = expression();
		if (expression_error)
			goto qwhat;
		
		ignore_blanks();			// all done
		t_SetTone(freq, duration);
		goto run_next_statement;
	}


beep:
	if (T_NUM_TONE_CHS == 0)		// if no tone channels...
		goto qsorry;
		
	t_SetTone(BEEP_FREQ, BEEP_DURATION);
	while (t_CheckToneStatus())  ;
	goto run_next_statement;
	
	
test:
	t_Test();
	goto run_next_statement;

}


/*
 * Routines to support filename authentication
 */

/*
 * isValidFnChar      tests char passed as argument c, returns TRUE if char is legal in a filename
 */
static int		isValidFnChar(char  c)
{
  if( c >= '0' && c <= '9' ) return TRUE; // number
  if( c >= 'A' && c <= 'Z' ) return TRUE; // LETTER
  if( c >= 'a' && c <= 'z' ) return TRUE; // letter (for completeness)
  if( c == '_' ) return TRUE;
  if( c == '+' ) return TRUE;
  if( c == '.' ) return TRUE;
  if( c == '~' ) return TRUE;  // Window~1.txt

  return FALSE;
}



/*
 * filenameWord      parse text buffer for a legal file name
 * 
 * If this code finds a valid filename in the text buffer, it copies the file name
 * to the tempfilename buffer and returns S_OK.  If this code detects an error,
 * it returns a suitable error code and clears the tempfilename buffer.
 * 
 * Text buffer is assumed to hold a file name protected by single- or double-
 * quotes; this avoids the automatic conversion of chars to uppercase.
 */
static DATA_SIZE			filenameWord(void)
{
	unsigned char				*ptr;
	unsigned char				quotemark;
	int							numchars;
	
	numchars = 0;
	ptr = tempfilename;
	*ptr = '\0';				// start by clearing the temp filename buffer
	
// Scan text buffer for first single- or double-quote
	ignore_blanks();
	if (*txtpos == '\'' || *txtpos == '\"')		// if found a quote mark...
	{
		quotemark = *txtpos;
	}
	else 
	{
		return  E_BAD_FILE_NAME;
	}
	txtpos++;					// this should be first char of filename
	
// Step through text buffer until finding matching quote mark, illegal char, or end of line
	while (isValidFnChar(*txtpos))
	{
		if (numchars == MAX_LEN_FILENAME)		// if already hit largest file name...
		{
			*tempfilename = '\0';			// erase the file name we found so far
			return  E_BAD_FILE_NAME;		// show there's a problem
		}
		*ptr = *txtpos;
		txtpos++;
		ptr++;
		numchars++;
	}
	
	if (*txtpos != quotemark)			// anything besides a matching quote mark is bad
	{
		return  E_BAD_FILE_NAME;
	}
	txtpos++;							// move past the quote mark
	*ptr = '\0';						// mark end of file name in temp buffer
	return  S_OK;
}



/*
 * Sorry, but this code makes no sense to me.  I've commented it out but left it in
 * the code, in case I should reach enlightenment.   KEL  23 Aug 23
 */
#if 0
static char     *filenameWord(void)
{
  // SDL - I wasn't sure if this functionality existed above, so I figured i'd put it here
  unsigned char 	*ret;
  
  ret = txtpos;
  expression_error = 0;

  // make sure there are no quotes or spaces, search for valid characters
  //while(*txtpos == SPACE || *txtpos == TAB || *txtpos == SQUOTE || *txtpos == DQUOTE ) txtpos++;
  while( !isValidFnChar( *txtpos )) txtpos++;
  ret = txtpos;

  if( *ret == '\0' ) {
    expression_error = 1;
    return   (char *)ret;
  }

  // now, find the next nonfnchar
  txtpos++;
  while (isValidFnChar( *txtpos ))  txtpos++;
  if (txtpos != ret)  *txtpos = '\0';

  // set the error code if we've got no string
  if (*ret == '\0')
  {
    expression_error = 1;
  }

  return  (char *)ret;
}
#endif			// if 0

/***********************************************************/
void setup()
{
/*
 * Do not set timer rate!  The target should have already set the timer rate
 * to 1 msec, so the system tic timer is running at that rate.
 */
 
	t_SetTone(BEEP_FREQ, BEEP_DURATION);		// short beep to announce we are here
	
	if (t_FileExistsQ(kAutorunFilename ))
	{
		program_end = program_start;
		rfp = t_OpenFile(kAutorunFilename, "r");
		t_SetInputStream(T_STREAM_FILE);
		inhibitOutput = TRUE;
		runAfterLoad = TRUE;
	}
	
	lockrangeend = BEYOND_VALID_LINENUM;		// mark program as unlocked for editing
	lockrangestart = BEYOND_VALID_LINENUM;
}


/***********************************************************/
static unsigned char breakcheck(void)
{
	if (t_ConsoleCharAvailable())			// if user pressed a key...
	{
		if (t_GetCharFromConsole() == CTRLC)	// always uses serial stream, ignores input stream assignment
		{
			return  TRUE;
		}
	}
	
	if (t_CheckForHWBreak())				// if user issued hardware break...
		return  TRUE;
		
	return  FALSE;
}
/***********************************************************/
static int  inchar()
{
	int			c;
  
	c = t_GetChar();
	if (rfp && c == EOF)				// if just read EOF from input file...
	{
		t_CloseFile(rfp);			// close the file for read
		rfp = 0;					// clear the file pointer
		t_SetInputStream(T_STREAM_SERIAL);	// switch input stream to serial port
		inhibitOutput = FALSE;		// let user see what she's typing
		c = NL;						// this will trigger a prompt following LOAD completion
		if (runAfterLoad)			// if auto-run file after loading...
		{
			runAfterLoad = FALSE;	// done with the load
			triggerRun = TRUE;		// trigger execution in warmstart
		}
	}
	  
  // translation for desktop systems
  if (c == LF) c = CR;

  return  c;
}

/***********************************************************/
static void outchar(unsigned char c)
{
  if (inhibitOutput) return;

  t_OutChar(c);
}


/*
 * TinyBasicLike main() entry point
 */
int main( int argc, char ** argv )
{
	do
	{
		forcereboot = FALSE;
		t_ColdBoot();
		
		//srand(1234567);
	
		printstr("\n");
		printmsg(t_TargetIDMsg);
		printmsg(initmsg);
		printstr("\n");

		t_WarmBoot();
		setup();

		loop();
    
/*
 * We reach this point on leaving the interpreter loop, usually because the user entered
 * the 'BYE' (forcereboot = FALSE) or 'REBOOT' (forcereboot = TRUE) commands.
 */
		if (forcereboot)
		{
			t_Shutdown();			// perform whatever tasks the target must do to shutdown
			t_ForceHWReset();		// now force a hardware reset; control will not return from this function
		}
		
	}  while (1);
}

