/PROG  HS_MOTION_BACKEND
/ATTR
OWNER		= MNEDITOR;
COMMENT		= "Motion using reg";
PROG_SIZE	= 2064;
CREATE		= DATE 17-10-19  TIME 13:19:58;
MODIFIED	= DATE 17-10-20  TIME 11:30:06;
FILE_NAME	= ;
VERSION		= 0;
LINE_COUNT	= 89;
MEMORY_SIZE	= 2468;
PROTECT		= READ_WRITE;
TCD:  STACK_SIZE	= 0,
      TASK_PRIORITY	= 50,
      TIME_SLICE	= 0,
      BUSY_LAMP_OFF	= 0,
      ABORT_REQUEST	= 0,
      PAUSE_REQUEST	= 0;
DEFAULT_GROUP	= 1,*,*,*,*;
CONTROL_CODE	= 00000000 00000000;
/MN
    :   ;
    : LBL[1];
    :  !cache karel pos in temp preg ;
    :  PR[2:pos cache]=PR[41:pos]    ;
    : R[7] = 0;
    : !track number of distinct motion instructions;
    : R[8] = R[8] + 1;
    :  !move to point with joint optimized trajectory;
    :  J PR[2] 100% CNT100 ;
    : IF R[7] <> 0, JMP LBL[1];
    : WAIT 0.05sec;
    : JMP LBL[1];
    :  ABORT ;
    :   ;/POS
/END
