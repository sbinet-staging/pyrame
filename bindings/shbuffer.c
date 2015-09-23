/*
Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
This file is part of Pyrame.

Pyrame is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pyrame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Pyrame.  If not, see <http://www.gnu.org/licenses/>
*/

#include "bindpyrame.h"

//*************************** SEMAPHORES *********************************

int open_semaphore(key_t key, unsigned char create,int setval) {
  int result;
  int semaphore;
  if (create) {
    semaphore=semget(key,1,IPC_CREAT|IPC_EXCL|0666);
    if ((semaphore==-1) && (errno==EEXIST)) {
	semaphore=semget(key,1,0);
	semctl(semaphore,0,IPC_RMID);
	semaphore=semget(key,1,IPC_CREAT|IPC_EXCL|0666);
      }
  } else {
    semaphore=semget(key,1,0);
  }
  if (semaphore==-1) {
    printf("cant open semaphore with key %d\n",key);
    perror("semget");
    exit(1);
  }
  if (create) {
    result=semctl(semaphore,0,SETVAL,setval);
    if (result==-1) {
      perror("semctl");
      exit(1);
    }
  }
  return semaphore;
}

void destroy_semaphore(int semaphore) {
  semctl(semaphore,0,IPC_RMID);
}

//acquire the semaphore
void P(int semid) {
  struct sembuf op;
  int result;
  op.sem_num=0;
  op.sem_op=-1;
  op.sem_flg=0;
  result=semop(semid,&op,1);
  if (result==-1) {
    perror("semop");
    exit(1);
  }
  //printf("P");
}

//free the semaphore
void V(int semid) {
  struct sembuf op;
  int result;
  op.sem_num=0;
  op.sem_op=1;
  op.sem_flg=0;
  result=semop(semid,&op,1);
  if (result==-1) {
    perror("semop");
    exit(1);
  }
  //printf("V");
}

int semread(int semid) {
  int res;
  res=semctl(semid,0,GETVAL,0);
  if (res==-1) {
    perror("semctl");
    return -1;
  } else {
    return res;
  }
}


//*********************** SHARED MEMORY ******************************** 

int open_shmem(key_t key,int create) {
  int shmid;
  if (create) {
    shmid=shmget(key,8192,IPC_CREAT|0666);
  } else {
    shmid=shmget(key,8192,0);
  }
  if (shmid==-1) {
    printf("cant open shmem with key %d\n",key);
    perror("shmget");
    exit(1);
  }
  return shmid;
}

void * get_shmem_pointer(int shmid) {
  return shmat(shmid,(void *)0,0);
}

void destroy_shmem(int shmid,void *shdata) {
  shmdt(shdata);
  shmctl(shmid,IPC_RMID,NULL);
}


//************************* SHBUFFER **************************************

struct shbuffer * open_shbuffer(int streamid,int create) {
  struct shbuffer *result=malloc(sizeof(struct shbuffer));
  memset(result,0,sizeof(struct shbuffer));
  result->full_semid=open_semaphore((key_t)((9010+streamid)*10+1),create,0);
  result->empty_semid=open_semaphore((key_t)((9010+streamid)*10+2),create,1);
  result->mutex_semid=open_semaphore((key_t)((9010+streamid)*10+3),create,1);
  result->ready_semid=open_semaphore((key_t)((9010+streamid)*10+4),create,0);
  result->shmid=open_shmem((key_t)(9010+streamid),create);
  result->shdata=get_shmem_pointer(result->shmid);
  result->flushed=1;
  result->tmp_size=0;
  result->tmp=malloc(SHARED_BUFFER_SIZE*sizeof(char));
  result->data_size=0;
  return result;
}

void close_shbuffer(struct shbuffer *shbuf) {
  destroy_shmem(shbuf->shmid,shbuf->shdata);
  destroy_semaphore(shbuf->full_semid);
  destroy_semaphore(shbuf->empty_semid);
  destroy_semaphore(shbuf->mutex_semid);
  destroy_semaphore(shbuf->ready_semid);
  free(shbuf->tmp);
  free(shbuf);
}

int read_shbuffer(struct shbuffer *shbuf,char *buffer) {
  P(shbuf->full_semid);
  P(shbuf->mutex_semid);
  memcpy(buffer,shbuf->shdata,SHARED_BUFFER_SIZE);
  V(shbuf->mutex_semid);
  V(shbuf->empty_semid);
  return SHARED_BUFFER_SIZE;
}

int isready_shbuffer(struct shbuffer *shbuf) {
  return semread(shbuf->ready_semid);
}

void ready_shbuffer(struct shbuffer *shbuf) {
  int result;
  result=semread(shbuf->ready_semid);
  if (result==0)
    V(shbuf->ready_semid);
}

void unready_shbuffer(struct shbuffer *shbuf) {
  int result;
  result=semread(shbuf->ready_semid);
  if (result==1)
    P(shbuf->ready_semid);
}



int write_shbuffer(struct shbuffer *shbuf,char *buffer,int size) {
  int fill_size;

  if (shbuf->flushed) { 
    P(shbuf->empty_semid);
    P(shbuf->mutex_semid);
    if (shbuf->tmp_size) {
      memcpy(shbuf->shdata,shbuf->tmp,shbuf->tmp_size);
      shbuf->data_size=shbuf->tmp_size;
      shbuf->tmp_size=0;
    }
    shbuf->flushed=0;
  }
  if ((shbuf->data_size+size)<=SHARED_BUFFER_SIZE) {
    //the data is too short to fill the entire shdata so just copy and wait another packet
    memcpy(shbuf->shdata+shbuf->data_size,buffer,size);
    shbuf->data_size+=size;
  }  else {
    //the packet size exceed the shdata size so copy the overrun in tmp
    fill_size=SHARED_BUFFER_SIZE-shbuf->data_size;
    memcpy(shbuf->shdata+shbuf->data_size,buffer,fill_size);
    shbuf->tmp_size=size-fill_size;
    memcpy(shbuf->tmp,buffer+fill_size,shbuf->tmp_size);
    shbuf->data_size=0;
    //the shmem is full release it
    shbuf->flushed=1;
    V(shbuf->mutex_semid);
    V(shbuf->full_semid);
  }
  return size;
}
