/*
MIT License

Copyright(c) 2022 e-sailing

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions :

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/*
 * @file
 * Aplication 
   -run on LG-ESS
   -publish LG-ESS data to an mqtt broker
   test
		cat testLGESS.txt | pipe2mqtt 192.168.xxx.xxx
 */
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#include <mqtt.h>
#include <posix_sockets.h>
#include <pipe2mqtt.h>


/**
 * @brief The function that would be called whenever a PUBLISH is received.
 *
 * @note This function is not used in this example.
 */
void publish_callback(void** unused, struct mqtt_response_publish *published);

/**
 * @brief The client's refresher. This function triggers back-end routines to
 *        handle ingress/egress traffic to the broker.
 *
 * @note All this function needs to do is call \ref __mqtt_recv and
 *       \ref __mqtt_send every so often. I've picked 100 ms meaning that
 *       client ingress/egress traffic will be handled every 100 ms.
 */
void* client_refresher(void* client);

/**
 * @brief Safelty closes the \p sockfd and cancels the \p client_daemon before \c exit.
 */
void exit_example(int status, int sockfd, pthread_t *client_daemon);

/**
 * A simple program to that publishes the current time whenever ENTER is pressed.
 */
int main(int argc, const char *argv[])
{
    const char* addr;
    const char* port;
    const char* topic;

    /* get address (argv[1] if present) */
    if (argc > 1) {
        addr = argv[1];
    } else {
        addr = "test.mosquitto.org";
    }

    /* get port number (argv[2] if present) */
    if (argc > 2) {
        port = argv[2];
    } else {
        port = "1883";
    }

    /* get the topic name to publish */
    if (argc > 3) {
        topic = argv[3];
    } else {
        topic = "lgess";
    }

    /* open the non-blocking TCP socket (connecting to the broker) */
    int sockfd = open_nb_socket(addr, port);

    if (sockfd == -1) {
        perror("Failed to open socket: ");
        exit_example(EXIT_FAILURE, sockfd, NULL);
    }

    /* setup a client */
    struct mqtt_client client;
    uint8_t sendbuf[2048]; /* sendbuf should be large enough to hold multiple whole mqtt messages */
    uint8_t recvbuf[1024]; /* recvbuf should be large enough any whole mqtt message expected to be received */
    mqtt_init(&client, sockfd, sendbuf, sizeof(sendbuf), recvbuf, sizeof(recvbuf), publish_callback);
    /* Create an anonymous session */
    const char* client_id = NULL;
    /* Ensure we have a clean session */
    uint8_t connect_flags = MQTT_CONNECT_CLEAN_SESSION;
    /* Send connection request to the broker. */
    mqtt_connect(&client, client_id, NULL, NULL, 0, NULL, NULL, connect_flags, 400);

    /* check that we don't have any errors */
    if (client.error != MQTT_OK) {
        fprintf(stderr, "error: %s\n", mqtt_error_str(client.error));
        exit_example(EXIT_FAILURE, sockfd, NULL);
    }

    /* start a thread to refresh the client (handle egress and ingree client traffic) */
    pthread_t client_daemon;
    if(pthread_create(&client_daemon, NULL, client_refresher, &client)) {
        fprintf(stderr, "Failed to start client daemon.\n");
        exit_example(EXIT_FAILURE, sockfd, NULL);

    }
    char fullTopic[40];
    FILE *in = stdin;
	int space1=0;
	int space2=0;

    while (dataLen>-1){
        if (get_line(in)>0)
        {
            if (get_json()>0){
                if (sendBufferReady==1){
					//bms raw / standard
					space1++;
					if (space1>50){
						space1=0;
						sprintf(fullTopic,"%s/bms",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

						sprintf(sendBuffer,"%.2f",gridActivePower);
						sprintf(fullTopic,"%s/gridActivePower",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
						
						sprintf(sendBuffer,"%.2f",pvPower);
						sprintf(fullTopic,"%s/pvPower",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
						
						sprintf(sendBuffer,"%.0f",pvSoc);
						sprintf(fullTopic,"%s/pvSoc",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
						
						sprintf(sendBuffer,"%d",pvBatPower);
						sprintf(fullTopic,"%s/pvBatPower",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
						
						sprintf(sendBuffer,"%.2f",homePower);
						sprintf(fullTopic,"%s/homePower",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
					}
					
					//evcc
                    sprintf(sendBuffer,"%.2f",pvPower);
                    mqtt_publish(&client, "openWB/set/pv/1/W", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
                    
                    sprintf(sendBuffer,"%d",pvBatPower);
                    mqtt_publish(&client, "openWB/set/houseBattery/W", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.0f",pvSoc);
                    mqtt_publish(&client, "openWB/set/houseBattery/%Soc", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
                    					
					//openWB
                    sprintf(sendBuffer,"%.2f",pvPower);
                    mqtt_publish(&client, "evcc/input/site/pvPower", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
                    
                    sprintf(sendBuffer,"%d",pvBatPower);
                    mqtt_publish(&client, "evcc/input/site/batteryPower", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.0f",pvSoc);
                    mqtt_publish(&client, "evcc/input/site/batterySoC", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);					
                }
                else if (sendBufferReady==2){
					//meter all
					space2++;
					if (space2>100){
						space2=0;
						sprintf(sendBuffer,"{\"import\":%.2f,",gridActiveImport);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"export\":%.2f,",gridActiveExport);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"V1\":%.1f,",gridVoltage1);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"V2\":%.1f,",gridVoltage2);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"V3\":%.1f,",gridVoltage3);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"power\":%.2f,",gridActivePower);
						sprintf(&sendBuffer[strlen(sendBuffer)],"\"freq\":%.2f}",gridFrequency);
						sprintf(fullTopic,"%s/meter",topic);
						mqtt_publish(&client, fullTopic, sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
					}
					
					//evcc                   
                    sprintf(sendBuffer,"%.2f",gridActivePower);
                    mqtt_publish(&client, "evcc/input/site/gridPower", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

					//openWB					
                    sprintf(sendBuffer,"%.0f",gridActivePower);
                    mqtt_publish(&client, "openWB/set/evu/W", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.2f",gridActiveImport);
                    mqtt_publish(&client, "openWB/set/evu/WhImported", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.2f",gridActiveExport);
                    mqtt_publish(&client, "openWB/set/evu/WhExported", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.1f",gridVoltage1);
                    mqtt_publish(&client, "openWB/set/evu/VPhase1", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.1f",gridVoltage2);
                    mqtt_publish(&client, "openWB/set/evu/VPhase2", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);

                    sprintf(sendBuffer,"%.1f",gridVoltage3);					
                    mqtt_publish(&client, "openWB/set/evu/VPhase3", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);
					
                    sprintf(sendBuffer,"%.2f",gridFrequency);					
                    mqtt_publish(&client, "openWB/set/evu/HzFrequenz", sendBuffer, strlen(sendBuffer), MQTT_PUBLISH_QOS_0);					
                }
                
                
                //printf(sendBuffer);
                //printf("\n");
                sleep(1); // only needed for testing with a file

                // check for errors
                if (client.error != MQTT_OK) {
                    fprintf(stderr, "error: %s\n", mqtt_error_str(client.error));
                    exit_example(EXIT_FAILURE, sockfd, &client_daemon);
                }
                sendBuffer[0]='\0';
                sendBufferReady=0;
            }
        }
        if (feof(in)){
            printf("\n");
            break;
        } 
    }
    

    /* //start publishing the time 
    printf("%s is ready to begin publishing the time.\n", argv[0]);
    printf("Press ENTER to publish the current time.\n");
    printf("Press CTRL-D (or any other key) to exit.\n\n");
    while(fgetc(stdin) == '\n') {
        // get the current time
        time_t timer;
        time(&timer);
        struct tm* tm_info = localtime(&timer);
        char timebuf[26];
        strftime(timebuf, 26, "%Y-%m-%d %H:%M:%S", tm_info);

        // print a message
        char application_message[256];
        snprintf(application_message, sizeof(application_message), "The time is %s", timebuf);
        printf("%s published : \"%s\"", argv[0], application_message);

        // publish the time
        mqtt_publish(&client, topic, application_message, strlen(application_message) + 1, MQTT_PUBLISH_QOS_0);

        // check for errors
        if (client.error != MQTT_OK) {
            fprintf(stderr, "error: %s\n", mqtt_error_str(client.error));
            exit_example(EXIT_FAILURE, sockfd, &client_daemon);
        }
    }
    */

    /* disconnect */
    printf("\n%s disconnecting from %s\n", argv[0], addr);
    sleep(1);

    /* exit */
    exit_example(EXIT_SUCCESS, sockfd, &client_daemon);
}

void exit_example(int status, int sockfd, pthread_t *client_daemon)
{
    if (sockfd != -1) close(sockfd);
    if (client_daemon != NULL) pthread_cancel(*client_daemon);
    exit(status);
}



void publish_callback(void** unused, struct mqtt_response_publish *published)
{
    /* not used in this example */
}

void* client_refresher(void* client)
{
    while(1)
    {
        mqtt_sync((struct mqtt_client*) client);
        usleep(100000U);
    }
    return NULL;
}
