/*
 * TinyBasicLike.h      header file for global definitions used by TBL and target code
 */
 
 #ifndef  TINYBASICLIKE_H
 #define  TINYBASICLIKE_H
 
 
#ifndef  FALSE
#define  FALSE   0
#define  TRUE    !FALSE
#endif



/*
 * Global error codes, mostly for file I/O
 */
#define  S_OK							0
#define  E_FILE_NOT_FOUND  				1
#define  E_BAD_FILE_NAME				2
#define  E_NO_ROOM_IN_FLASH				3
#define  E_FAILED_TO_CREATE_FILE		4
#define  E_COULD_NOT_ADD_TIMER			5
#define  E_DIVIDE_BY_ZERO				6
#define  E_MISSING_CLOSING_PAREN		7
#define  E_ADDR_FUNC_REQUIRES_VAR_ARG	8
#define  E_UNKNOWN_VAR_PORT_FUNC		9
#define  E_MISSING_OPEN_PAREN			10
#define  E_BAD_CHAR_CONSTANT_SQUOTE		11
#define  E_ZERO_ARG_FOR_RAND			12
#define  E_UNKNOWN_CHAR_OR_OPERATOR		13

#include <stdint.h>

//#ifndef DATA_SIZE
#define DATA_SIZE	long
//#endif

#ifndef T_PROGSPACE_SIZE
#define  T_PROGSPACE_SIZE			32000
#endif

#ifndef MAX_LEN_FILENAME
#define  MAX_LEN_FILENAME			15
#endif

#ifndef DATA_SIZE_MAX
#define  DATA_SIZE_MAX				sizeof(long)
#endif

#ifndef UDATA_SIZE
#define  UDATA_SIZE					unsigned long
#endif

#ifndef T_STREAM_FILE
#define  T_STREAM_FILE				0
#endif

#ifndef T_STREAM_SERIAL
#define  T_STREAM_SERIAL			0
#endif

#ifndef T_SUPPORTS_FILES
#define  T_SUPPORTS_FILES			0	//TRUE=1 FALSE=0
#endif


#ifndef T_NUM_TONE_CHS
#define  T_NUM_TONE_CHS			0	//TRUE=1 FALSE=0
#endif



/*
 * Global print routines, mostly for debug
 */
void     			printmsg(const unsigned char *msg);		// print const strings
void				printstr(char  *str);					// print strings from RAM
void				printnum(DATA_SIZE  num,  int  radix);


/*
 * Define structures for holding FOR loop, GOSUB, and variable data
 */
struct		stack_for_frame
{
	char 				frame_type;
	char 				for_var;
	DATA_SIZE			terminal;
	DATA_SIZE			step;
	unsigned char 		*current_line;
	unsigned char 		*txtpos;
};

struct		stack_gosub_frame
{
	char 				frame_type;
	unsigned char 		*current_line;
	unsigned char 		*txtpos;
};

struct		var_name_addr
{
	unsigned char		basename;
	DATA_SIZE			*addr;
};

	

/*
 * Defines for allocating RAM buffers for program storage, variables, and stacks
 */
#define  MAX_FOR_FRAMES				5		/* maximum FOR stacks that the stack can hold */


/*
 * The stack holds FOR frames and is also used for holding chars during numeric output by PRINT.
 */
#define STACK_SIZE  ((sizeof(struct stack_for_frame) * MAX_FOR_FRAMES) + (sizeof(DATA_SIZE)*2) + 20)
#define VAR_SIZE 	(sizeof(DATA_SIZE)) 	/* Size of variable space in bytes */

#define  ARRAY_X_SIZE			20
#define  ARRAY_Y_SIZE			20
//                                     --- A-W ---        ---------- X, Y, Z -------     padding
#define  TOTAL_VARIABLE_SPACE		(((23 * VAR_SIZE) + (3 * ARRAY_X_SIZE * ARRAY_Y_SIZE) + 1)    * VAR_SIZE)

#define  TOTAL_RAM_REQUIRED		(T_PROGSPACE_SIZE + STACK_SIZE + TOTAL_VARIABLE_SPACE)


/*
 * Defines for printing radix, used by printnum()
 */
#define  RADIX_HEX				16
#define  RADIX_DECIMAL			10
#define  RADIX_CHAR				99			/* output a value as an ASCII char */



/*
 * Define the default name for the file to run automatically on startup.
 */
#define  kAutorunFilename			"autorun.bas"
/*
 * dummy things
 */
 const unsigned char         ports_tab[] =
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
DATA_SIZE               t_ReadPort(int  index)
{
        DATA_SIZE                       a;

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

int	t_CheckToneStatus(void)
{

		return 0;
}












 #endif
 
