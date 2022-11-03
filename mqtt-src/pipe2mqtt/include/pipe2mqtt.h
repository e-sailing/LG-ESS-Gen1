#include <stdio.h>
#include <unistd.h>
#include <string.h>

char data[200];
char data0[200];
char data1[200];
char sendBuffer[1000];
int sendBufferReady = 0;
int error0=1;
int dataLen;
int dataLen0;
int dataLen1;
char pid[8];
char pid0[8];
char pid1[8];
int  rw;
char writeData07;
char lastWriteData07;
double gridActiveImport;
double gridActiveExport;
double gridVoltage1;
double gridVoltage2;
double gridVoltage3;
double gridActivePower;
double gridFrequency;

double pvPower;
double pvSoc;
int pvBatPower;
double homePower;

int get_line(FILE *fp)
{
    int  pidCounter=0;
    int  dataCounter=0;
    int  byteCounter=0;
    char c;
    int cc;
    int  counter=0;
    
    int status=1;

    while ((cc = getc(fp)) != EOF)
    {
        c=(char)cc;
        if (c=='\n') {
            if (status==7) {
                dataLen = byteCounter;
            }
            else {
                //printf("return 0\n");
                dataLen = 0;
            }
            return dataLen;
        }

        counter++;
        if (status==1){
            if (c == '[') {
                status=2;
                counter=0;
            }
            //printf("status1");
        }
        else if (status==2){
            if (counter==4){
                status=3;
            }
        }        
        else if (status==3) {        
            if (c!=' ')
            {
                pid[pidCounter]=c;
                pidCounter++;
            }
            if (counter==9) {
                pid[pidCounter]='\0';
                status=4;
            }
        }
        else if (status==4){
            if (counter==12) {
                rw=c;
                status=5;
            }
        }    
        else if (status==5){
            if (c=='"') {
                status=6;
            }
        }
        else if (status==6){
            if (c=='"') {
                status=7;
            }
            else if (!(c=='\\' || c=='x')){
                if (dataCounter==0){
                    if (c >= '0' && c <= '9') c = c - '0';
                    else if (c >= 'a' && c <='f') c = c - 'a' + 10;
                    data[byteCounter] = c << 4;
                    dataCounter++;
                }
                else{
                    if (c >= '0' && c <= '9') c = c - '0';
                    else if (c >= 'a' && c <='f') c = c - 'a' + 10;
                    data[byteCounter] += c;
                    dataCounter--;
                    byteCounter++;
                }
            }
        }
    }
    dataLen = 0;
    return dataLen;
}

void format_bms() {
    int int32[46];
    int pos=0;


    sprintf(sendBuffer,"{\"raw\":[");
    pos = strlen(sendBuffer);
    if (dataLen1==189){

        // for (int i=0;i<189;i++){
        // printf("%i;", data1[i]);
        // }
        // printf("\n");

        for (int i=0;i<45;i++){
            //printf("%d: %x %x %x %x\n",i,data1[3+i*4],data1[4+i*4],data1[5+i*4],data1[6+i*4]);
            int32[i] = (data1[3+i*4]<<24) | (data1[4+i*4]<<16) | (data1[5+i*4]<<8) | data1[6+i*4];
            sprintf(&sendBuffer[strlen(sendBuffer)],"%ld,", int32[i]);
        }
        //sprintf(&sendBuffer[strlen(sendBuffer)],"%ld],", int32[45]);
        sprintf(&sendBuffer[strlen(sendBuffer)],"%ld]}", int32[45]);

        pvPower = ((int32[10] + int32[13]) * 0.99)-100;
        if (pvPower<0) pvPower = 0;
        pvSoc = (int32[26] - 45) * 100 / 905;
        pvBatPower = int32[19];
        homePower = gridActivePower+pvPower+pvBatPower;

        //sprintf(&sendBuffer[strlen(sendBuffer)],"\"pvPower\":%.0f,", pvPower);
        //sprintf(&sendBuffer[strlen(sendBuffer)],"\"pvSoc\":%.2f,", pvSoc);
        //sprintf(&sendBuffer[strlen(sendBuffer)],"\"pvBatPower\":%d,", pvBatPower);
        //sprintf(&sendBuffer[strlen(sendBuffer)],"\"homePower\":%.2f}", homePower);

        sendBufferReady=1;
        //printf(sendBuffer);
        //printf("\n");
    }
}

int format_imp_exp(){
    int int32=0;
    if (dataLen0==13){
        int32 = (data0[7]<<24) | (data0[8]<<16) | (data0[9]<<8) | data0[10];
    }
    else error0=1;
    return int32;
}

int format_voltage(){
    int int16=0;
    if (dataLen0==9){
        int16=data0[5]*256+data0[6];
    }
    else error0=1;
    return int16;
}

int format_power(){
    int int32=0;
    if (dataLen0==9){
        int32 = (data0[3]<<24) | (data0[4]<<16) | (data0[5]<<8) | data0[6];
        gridActivePower = int32/100;
    }
    else error0=1;
    return int32;
}

int format_hz(){
    int int32=0;
    if (dataLen0==7){
        int32 = data0[3]*256+data0[4];
    }
    else error0=1;

    if (error0==0) sendBufferReady=2;
    error0=0;
	return int32;
}

int get_json()
{
    //printf("%s;%c;",pid,rw);
    //for (int i=0;i<dataLen;i++){
    //    printf("%i;", data[i]);
    //}
    //printf("\n");
    if (rw=='r'){
        if (strcmp(pid,pid0)==0){
            memcpy(&data0[dataLen0], data, dataLen);
            dataLen0+=dataLen;
        }
        else if (strcmp(pid,pid1)==0){
            memcpy(&data1[dataLen1], data, dataLen);
            dataLen1+=dataLen;
        }
    }
    if (rw=='w'){
        if (data[7]==0xb8) {
            if (strcmp(pid,pid1)!=0){
                strncpy(pid1, pid, 7);
            }
        }
        else if ((data[7]==0x09) || (data[7]==0xc8) || (data[7]==0x2f) || (data[7]==0xef) || (data[7]==0xee) || (data[7]==0x2b) || (data[7]==0xe7)) {
            if (strcmp(pid,pid0)!=0){    
                strncpy(pid0, pid, 8);
            }
            writeData07=data[7];
        }

        if (strcmp(pid,pid1)==0){
            format_bms();
            data1[0]='\0';
            dataLen1=0;
        }
        if (strcmp(pid,pid0)==0){
            if (lastWriteData07==0x09)      gridActiveImport=format_imp_exp()/100.;
            else if (lastWriteData07==0xc8) gridActiveExport=format_imp_exp()/100.;
            else if (lastWriteData07==0x2f) gridVoltage1=format_voltage()/10.;
            else if (lastWriteData07==0xef) gridVoltage2=format_voltage()/10.;
            else if (lastWriteData07==0xee) gridVoltage3=format_voltage()/10.;
            else if (lastWriteData07==0x2b) gridActivePower=format_power()/100.;
            else if (lastWriteData07==0xe7) gridFrequency=format_hz()/100.;
            dataLen0=0;
            data0[0]='\0';
            lastWriteData07=writeData07;
        }
		
		
		double gridActiveExport;
double gridVoltage1;
double gridVoltage2;
double gridVoltage3;
double gridActivePower;
double gridFrequency;

		
    }
    return sendBufferReady;
}

int main(int argc, const char *argv[]);
