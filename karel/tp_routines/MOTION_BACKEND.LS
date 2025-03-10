/PROG  MOTION_BACKEND
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
    :  !initialize skip condition;
    :  SKIP CONDITION R[5:skip]<>0;
    :   ;
    :  LBL[1] ;
    :   ;
    :  !cache karel pos in temp preg ;
    :  PR[2:pos cache]=PR[41:pos]    ;
    :  ;
    :  !check for linear or joint motion;
    :  IF R[6:linear motion] = 0, JMP LBL[2];
    :  ;
    :  !move to point with linear trajectory;
    :  !if skip is triggered, execution will continue on the next line;
    :  !if skip is not triggered during motion, execution will continue on lbl 10;
    : L PR[2] 2000mm/sec CNT100 Skip,LBL[1]    ;
    : ;
    :  !current traj has been aborted;
    :  !re enable the skip condition;
    :  SKIP CONDITION R[5:skip]<>0;
    :   ;
    :  !abort if reg is set to anything but 1;
    :  IF R[5:skip]<>1,JMP LBL[999] ;
    :   ;
    :  !skip "signal" has been consumed;
    : R[5: skip] = 0 ;
    :  !lookup next target pos;
    :  JMP LBL[1] ;
    :  ;
    :  LBL[2];
    :  !move to point with joint optimized trajectory;
    :  !if skip is triggered, execution will continue on the next line;
    :  !if skip is not triggered during motion, execution will continue on lbl 10;
    : J PR[2] 100% CNT100 Skip,LBL[1]    ;
    :   ;
    :  !current traj has been aborted;
    :  !re enable the skip condition;
    :  SKIP CONDITION R[5:skip]<>0;
    :  !abort if reg is set to anything but 1;
    :  IF R[5:skip]<>1,JMP LBL[999] ;
    :  !skip "signal" has been consumed;
    :  R[5: skip] = 0 ;
    :  !lookup next target pos;
    :  JMP LBL[1] ;
    :   ;
    :  LBL[999:abort];
    :  ABORT ;
    :   ;/POS
/END
