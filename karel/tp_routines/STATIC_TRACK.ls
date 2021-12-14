/PROG  STATIC_TRACK
/ATTR
OWNER   = MNEDITOR;
COMMENT   = "FDPMMD//r0b";
PROG_SIZE = 1050;
CREATE    = DATE 18-01-21  TIME 12:00:00;
MODIFIED  = DATE 18-01-21  TIME 12:00:00;
FILE_NAME = ;
VERSION   = 0;
LINE_COUNT  = 30;
MEMORY_SIZE = 1310;
PROTECT   = READ_WRITE;
TCD:  STACK_SIZE  = 0,
      TASK_PRIORITY = 50,
      TIME_SLICE  = 0,
      BUSY_LAMP_OFF = 0,
      ABORT_REQUEST = 0,
      PAUSE_REQUEST = 0;
DEFAULT_GROUP = 1,*,*,*,*;
CONTROL_CODE  = 00000000 00000000;
/MN
    :  !Start stat tracking ;
    :  Track DPM[1] ;
    :L PR[40] 100mm/sec FINE    ;
    :   ;
    :  !Stop tracking ;
    :  !(will never reach this) ;
    :  Track End ;
/END
