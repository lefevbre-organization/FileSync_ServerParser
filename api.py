import logging
import requests 
import settings
import os
import utils 


## settigs 
settings.Settings.init() # Call only once

##check endpoint (bool)
def method_check(endpoint_to_check): 
    try: 
        print("Calling method_to_check")     
        response = requests.post(endpoint_to_check, data = {'key':'value'}, timeout=settings.MAX_TIMEOUT)
        print("Requesting method_check")    
        if (response.status_code == 200):
            print("The request of endpoint_to_check :  was a success!")
            # Code here will only run if the request is successful
            return True
        elif (response.status_code) == 404:
            print("endpoint_to_check: not found!")
                # Code here will react to failed requests
            return False
    except requests.RequestException as err:
        logging.error({"message": err})
        return False
        

    
## insert and updated

def method_post(log_action):
    
    companyid = log_action['idcompany']
    userid = log_action['iduser'] 
    
    aliases_str = ""
    if 'aliases' in log_action:
        aliases_str = log_action['aliases'] + "/"
        
    filesOpen  = None 
    
    ## if Renamed then 
    if "Renamed" in log_action['msg']:
        # if moved action
        if os.path.dirname(utils.Utils.extact_double_cuotes(log_action['msg'])) != os.path.dirname(log_action['object']):
            print('moving from folder')
            new_object = log_action['object']
            log_action['object']=utils.Utils.extact_double_cuotes(log_action['msg'])
            if method_delete(log_action):
                log_action['msg'] = "Copied (new)"
                log_action['object']= new_object
                method_post(log_action)
                return True
            else:
                logging.error("message method_delete fail: " + log_action['msg'] )
                
        else:
            # renamend action   
            #dirname = os.path.dirname(utils.Utils.extact_double_cuotes(log_action['msg']))
            dirname = f'{aliases_str}{os.path.dirname(utils.Utils.extact_double_cuotes(log_action["msg"]))}'
            filename = os.path.basename(utils.Utils.extact_double_cuotes(log_action['msg']))
            newfilename = os.path.basename(log_action['object'])
            value = "{\"path\": \"%s\",\"fileName\": \"%s\",\"idEntityType\": \"78\",\"idEntity\": \"1\", \"newFileName\": \"%s\"}" %(dirname, filename, newfilename)
            files = None
    ## Copied new   
    else:  
        

        dirname = f'{aliases_str}{os.path.dirname(log_action["object"])}'
        filename = os.path.basename(log_action['object']) 
                
        #filepath = settings.CUSTOMERS_SOURCE_BASE + "/" + log_action['idcompany']  + "/" + settings.ARCHIVE_FOLDER + "/" + log_action['object']
        filepath = f'{settings.CUSTOMERS_SOURCE_BASE}/{log_action["idcompany"]}/{settings.ARCHIVE_FOLDER}/{aliases_str}{log_action["object"]}'
        
        value="{\"path\": \"%s\",\"fileName\": \"%s\",\"idEntityType\": \"78\",\"idEntity\": \"1\"}" %(dirname, filename) 
        # passing files on copied new items
        
        try:
            filesOpen = {'fileData': open(filepath,'rb')}
        except IOError as e:
            logging.error({"message": e.strerror  + " - object: " + log_action['object']} )
            logging.error({"filepath ": filepath} )
            print({"filepath error: ": filepath} )
            return False
        
    data= ({'userId':userid,'companyId':companyid,'document':value})

    endpoint_url = settings.ENDPOINT_TO_CHECK + "/rclone/document/save"
    
    for _ in range(settings.MAX_RETRIES):
        try:
            response = requests.post(endpoint_url, files=filesOpen, data=data, timeout=settings.MAX_TIMEOUT)
    
            print("Requesting method_post: " + log_action['object'])
            #raise requests.exceptions.Timeout
            if (response.status_code == 200):
                print("The request of method_post : " +  log_action['object'] + " was a success!")
                return True
                # Code here will only run if the request is successful
            elif (response.status_code) == 404:
                print("Result method_post: " +  log_action['object'] + " not found! " + str(response.reason))
                return False
                    # Code here will react to failed requests
            elif (response.status_code) == 401:
                print("Result method_post: " +  log_action['object'] + " error 401 " + str(response.reason))
                return False
                    # Code here will react to failed request        
            elif (response.status_code) == 400:
                print("Result method_post: " +  log_action['object'] + " error 400 " + str(response.reason))
                return False
                    # Code here will react to failed request
            elif (response.status_code) == 500:
                print("Result method_post: " +  log_action['object'] + " error 500 " + str(response.reason))
                #return False
                #ADDING MAX_RETRIES
                continue
                    # Code here will react to failed request
            elif (response.status_code) == 504:
                print("Result method_post: " +  log_action['object'] + " error 504 " + str(response.reason))
                return False
                    # Code here will react to failed request
            else:
                print("other error")
                return False
                #break
        except requests.Timeout as err:
            logging.error({"message": err})
            continue
            #return False
        except requests.RequestException as err:
            logging.error({"message": err})
            #pass
        finally: 
            if filesOpen is not None:         
                filesOpen['fileData'].close()
        
        return False

    
def method_delete(log_action): 

    aliases_str = ""
    if 'aliases' in log_action:
        aliases_str = log_action['aliases'] + "/"
    
    companyid = log_action['idcompany']
    userid = log_action['iduser']
    #dirname = os.path.dirname(log_action['object'])
    dirname= f'{aliases_str}{os.path.dirname(log_action["object"])}'
    filename = os.path.basename(log_action['object'])  
    
    value="{\"path\": \"%s\",\"fileName\": \"%s\",\"idEntityType\": \"78\",\"idEntity\": \"1\"}" %(dirname, filename)    
    data= ({'userId':userid,'companyId':companyid,'document':value})  
    
    endpoint_url = settings.ENDPOINT_TO_CHECK + "/rclone/document/delete"
    
    for _ in range(settings.MAX_RETRIES):
        try:
            response = requests.post(endpoint_url, data=data, timeout=settings.MAX_TIMEOUT )
            
            print("Requesting method_post: " + log_action['object'])
            
            if (response.status_code == 200):
                print("The request of method_post : " +  log_action['object'] + " was a success!")
                return True
                # Code here will only run if the request is successful
            elif (response.status_code) == 404:
                print("Result method_post: " +  log_action['object'] + " not found! " + str(response.reason))
                return False
                    # Code here will react to failed requests
            elif (response.status_code) == 401:
                print("Result method_post: " +  log_action['object'] + " error 401 " + str(response.reason))
                return False
                    # Code here will react to failed request        
            elif (response.status_code) == 400:
                print("Result method_post: " +  log_action['object'] + " error 400 " + str(response.reason))
                return False
                    # Code here will react to failed request
            elif (response.status_code) == 500:
                print("Result method_post: " +  log_action['object'] + " error 500 " + str(response.reason))
                #return False
                #ADDING MAX_RETRIES
                continue
                    # Code here will react to failed request
            elif (response.status_code) == 504:
                print("Result method_post: " +  log_action['object'] + " error 504 " + str(response.reason))
                return False
                    # Code here will react to failed request
            else:
                print("other error")
                return False
            
        except requests.Timeout as err:
            logging.error({"message": err})
            continue
        except requests.RequestException as err:
            logging.error({"message": err})
        #     pass
        return False
            

#method_post(log_action={})