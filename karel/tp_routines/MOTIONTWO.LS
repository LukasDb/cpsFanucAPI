/PROG  MOTIONTWO
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
    :  !set skip condition;
    :  SKIP CONDITION R[5:skip]<>0;
    :   ;
    :  LBL[10] ;
    :   ;
    :   ;
    :  !cache in temp preg ;
    :  PR[2:pos cache]=PR[1:pos]    ;
    :   ;
    :  !move to point ;
    :L PR[2] 5000mm/sec CNT100 Skip,LBL[10]    ;
    :  !current traj has been aborted;
    :  !re enable the skip condition;
    :  SKIP CONDITION R[5:ros skip]<>0;
    :   ;
    :  !abort if reg is set to anything but 1;
    :  IF R[5:ros skip]<>1,JMP LBL[999] ;
    :   ;
    :  !go back to idling;
    :  JMP LBL[10] ;
    :   ;
    :  LBL[999:abort];
    :  ABORT ;
    :   ;/POS
/END
