import pprint
import requests
import os
import sys
import json
import time
#function that calls all other tests
projectId=0
tjobId=0
essip=""
def e2etests():
	tormurl=sys.argv[1]
	#To check whether the TORM URL has been read correctly
	if tormurl[-1]!='/':
		tormurl=tormurl+'/'	

	print("TORM URL is: "+tormurl)
	#To check whether the TORM preloader page can successfully retrieved
	tests=["test_load_torm_home_preloader(tormurl)","test_load_torm_api_info(tormurl+\"/api/context/services/info\")","test_service_launch(tormurl)","test_create_new_project(tormurl+\"/api/project\")","test_create_new_tjob(tormurl+\"/api/tjob\")","test_run_tjob(tormurl)"]	
	#tests=["test_load_torm_home_preloader(tormurl)","test_load_torm_api_info(tormurl+\"/api/context/services/info\")","test_service_launch(tormurl)"]
	numtests=len(tests)
	testssuccess=0
	testsfailed=0	
	testsrun=0
	testsleft=numtests

	if numtests!=0:
		for i in range(len(tests)):
			testsrun+=1
			print("~~~~~~~~~~~~~~~")
			print("Running test "+str(testsrun)+" out of "+str(testsleft))
			status=eval(tests[i])
			if status=="success":
				testssuccess+=1
				print("Status: Success")
			if status=="failed":
				testsfailed+=1
				print("Status: Failed")
				break
			
	print("##############")
	print("_TESTS SUMMARY_")
	print("TOTAL TESTS RAN: "+str(testsrun))
	print("TOTAL TESTS SUCCEEDED: "+str(testssuccess))
	print("TOTAL TESTS FAILED: "+str(testsfailed))
	#status=test_load_torm_api_info(tormurl+"api/context/services/info") 

#Launch ESS service
def test_service_launch(tormurl):
		getinstancesurl=tormurl+"api/esm/services/instances"
		s=requests.Session()
		r = s.get(getinstancesurl)
		#print "Running services are"
		#print(r.text)
		if r.text=='[]':
			launchurl=tormurl+"api/esm/services/af7947d9-258b-4dd1-b1ca-17450db25ef7/prov"
			r1 = s.post(launchurl)
			#print("ESS launched with id")
			#print(r1.text)
			if len(r1.text)!=0:
				getessipurl=tormurl+"/api/esm/services/instances/"+r1.text
				print("Instances")
				r2=s.get(getinstancesurl)
				instances=json.loads(r2.text)
				print(instances)
				while 0==len(instances):
					time.sleep(5)
					r2=s.get(getinstancesurl)
					instances=json.loads(r2.text)
					print("Waiting for the launched instance to appear in instances set")
				while False==instances[0]["serviceReady"]:
					r2=s.get(getinstancesurl)
					instances=json.loads(r2.text)
					time.sleep(5)
					print("Waiting for service to be ready")
				if True==instances[0]["serviceReady"]:				
					r3=s.get(getessipurl)
					print("The IP address of ESS is")
					global essip
					essip=json.loads(r3.text)["serviceIp"]
					print(essip)
					return "success"

			else:	
				print("Length of instances array returned is 0")
				return "failed"
		else:
			print("Pre-launch issue: Some services are running before launching")
			return "failed"

def test_load_torm_home_preloader(tormurl):
		s=requests.Session()
		r = s.get(tormurl)
		#print(r.text)
		try:
			assert "Loading ElasTest..." in r.text
		except AssertionError:
			print("Test to load TORM home page prealoader failed")
			return "failed"
		return "success"

def test_load_torm_api_info(tormapiinfourl):
		s=requests.Session()
		r = s.get(tormapiinfourl)
		#print(r.text)
		try:
			assert "elasticSearchUrl" in r.text
		except AssertionError:
			print("Call to load elasticSearchUrl failed")
			return "failed"
		return "success"

def test_create_new_project(tormapicreateprojecturl):
		s=requests.Session()
		payload={"id": 0,"name": "E2E test ESS"}
		r = s.post(tormapicreateprojecturl,json=payload)
		#print(r.text)
		global projectId
		projectId=int(json.loads(r.text)["id"])
		try:
			assert "E2E test ESS" in r.text
		except AssertionError:
			print("New Project creation failed")
			return "failed"
		return "success"

def test_create_new_tjob(tormapicreatetjoburl):
		s=requests.Session()
		print("ProjectId is")
		print(projectId)
		payload={
  "id": 0,
  "name": "E2E tjob",
  "imageName": "dockernash/ess-e2e",
  "project": {
    "id": projectId,
    "name": "E2E test ESS",
    "suts": [],
    "tjobs": []
  },
  "tjobExecs": [],
  "parameters": [],
  "commands": "python tjob-request.py "+essip,
  "resultsPath": "",
  "execDashboardConfig": "{\"showComplexMetrics\":true,\"allMetricsFields\":{\"fieldsList\":[{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_cpu_totalUsage\",\"activated\":false,\"type\":\"cpu\",\"subtype\":\"totalUsage\",\"unit\":\"percent\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_memory_usage\",\"activated\":false,\"type\":\"memory\",\"subtype\":\"usage\",\"unit\":\"percent\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_memory_maxUsage\",\"activated\":false,\"type\":\"memory\",\"subtype\":\"maxUsage\",\"unit\":\"bytes\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_blkio_read_ps\",\"activated\":false,\"type\":\"blkio\",\"subtype\":\"read_ps\",\"unit\":\"bytes\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_blkio_write_ps\",\"activated\":false,\"type\":\"blkio\",\"subtype\":\"write_ps\",\"unit\":\"bytes\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_blkio_total_ps\",\"activated\":false,\"type\":\"blkio\",\"subtype\":\"total_ps\",\"unit\":\"bytes\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_rxBytes_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"rxBytes_ps\",\"unit\":\"amount/sec\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_rxErrors_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"rxErrors_ps\",\"unit\":\"amount/sec\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_rxPackets_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"rxPackets_ps\",\"unit\":\"amount/sec\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_txBytes_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"txBytes_ps\",\"unit\":\"amount/sec\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_txErrors_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"txErrors_ps\",\"unit\":\"amount/sec\"},{\"component\":\"\",\"stream\":\"et_dockbeat\",\"streamType\":\"composed_metrics\",\"name\":\"et_dockbeat_net_txPackets_ps\",\"activated\":false,\"type\":\"net\",\"subtype\":\"txPackets_ps\",\"unit\":\"amount/sec\"}]},\"allLogsTypes\":{\"logsList\":[{\"component\":\"test\",\"stream\":\"default_log\",\"streamType\":\"log\",\"name\":\"test_default_log_log\",\"activated\":true},{\"component\":\"sut\",\"stream\":\"default_log\",\"streamType\":\"log\",\"name\":\"sut_default_log_log\",\"activated\":true}]}}",
  "execDashboardConfigModel": {
    "showComplexMetrics": True,
    "allMetricsFields": {
      "fieldsList": [
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_cpu_totalUsage",
          "activated": False,
          "type": "cpu",
          "subtype": "totalUsage",
          "unit": "percent"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_memory_usage",
          "activated": False,
          "type": "memory",
          "subtype": "usage",
          "unit": "percent"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_memory_maxUsage",
          "activated": False,
          "type": "memory",
          "subtype": "maxUsage",
          "unit": "bytes"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_blkio_read_ps",
          "activated": False,
          "type": "blkio",
          "subtype": "read_ps",
          "unit": "bytes"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_blkio_write_ps",
          "activated": False,
          "type": "blkio",
          "subtype": "write_ps",
          "unit": "bytes"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_blkio_total_ps",
          "activated": False,
          "type": "blkio",
          "subtype": "total_ps",
          "unit": "bytes"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_rxBytes_ps",
          "activated": False,
          "type": "net",
          "subtype": "rxBytes_ps",
          "unit": "amount/sec"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_rxErrors_ps",
          "activated": False,
          "type": "net",
          "subtype": "rxErrors_ps",
          "unit": "amount/sec"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_rxPackets_ps",
          "activated": False,
          "type": "net",
          "subtype": "rxPackets_ps",
          "unit": "amount/sec"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_txBytes_ps",
          "activated": False,
          "type": "net",
          "subtype": "txBytes_ps",
          "unit": "amount/sec"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_txErrors_ps",
          "activated": False,
          "type": "net",
          "subtype": "txErrors_ps",
          "unit": "amount/sec"
        },
        {
          "component": "",
          "stream": "et_dockbeat",
          "streamType": "composed_metrics",
          "name": "et_dockbeat_net_txPackets_ps",
          "activated": False,
          "type": "net",
          "subtype": "txPackets_ps",
          "unit": "amount/sec"
        }
      ]
    },
    "allLogsTypes": {
      "logsList": [
        {
          "component": "test",
          "stream": "default_log",
          "streamType": "log",
          "name": "test_default_log_log",
          "activated": True
        },
        {
          "component": "sut",
          "stream": "default_log",
          "streamType": "log",
          "name": "sut_default_log_log",
          "activated": True
        }
      ]
    }
  },
  "esmServicesString": "[{\"id\":\"a1920b13-7d11-4ebc-a732-f86a108ea49c\",\"name\":\"EBS\",\"selected\":false},{\"id\":\"fe5e0531-b470-441f-9c69-721c2b4875f2\",\"name\":\"EDS\",\"selected\":false},{\"id\":\"af7947d9-258b-4dd1-b1ca-17450db25ef7\",\"name\":\"ESS\",\"selected\":true},{\"id\":\"29216b91-497c-43b7-a5c4-6613f13fa0e9\",\"name\":\"EUS\",\"selected\":false},{\"id\":\"bab3ae67-8c1d-46ec-a940-94183a443825\",\"name\":\"EMS\",\"selected\":false}]",
  "esmServices": [
    {
      "id": "a1920b13-7d11-4ebc-a732-f86a108ea49c",
      "name": "EBS",
      "selected": False
    },
    {
      "id": "fe5e0531-b470-441f-9c69-721c2b4875f2",
      "name": "EDS",
      "selected": False
    },
    {
      "id": "af7947d9-258b-4dd1-b1ca-17450db25ef7",
      "name": "ESS",
      "selected": True
    },
    {
      "id": "29216b91-497c-43b7-a5c4-6613f13fa0e9",
      "name": "EUS",
      "selected": False
    },
    {
      "id": "bab3ae67-8c1d-46ec-a940-94183a443825",
      "name": "EMS",
      "selected": False
    }
  ],
  "esmServicesChecked": 0
}
		#print(payload)
		r = s.post(tormapicreatetjoburl,json=payload)
		#print(r.text)
		global tjobId
		tjobId=int(json.loads(r.text)["id"])
		#print tjobId
		try:
			assert "E2E tjob" in r.text
		except AssertionError:
			print("New TJob creation failed")
			return "failed"
		return "success"

def test_run_tjob(tormurl):
		time.sleep(5)
		s=requests.Session()
		payload={"tJobParams": []}
		r = s.post(tormurl+"api/tjob/"+str(tjobId)+"/exec",json=payload)
		#print(r.text)
		
		try:
			assert "IN PROGRESS" in str(json.loads(r.text)["result"])
			exec_resp=s.get(tormurl+"api/tjob/"+str(tjobId)+"/exec/"+str(json.loads(r.text)["id"]))
			while ("IN PROGRESS" in str(json.loads(exec_resp.text)["result"])) or ("STARTING TSS" in str(json.loads(exec_resp.text)["result"]))  or ("EXECUTING TEST" in str(json.loads(exec_resp.text)["result"])) or ("WAITING" in str(json.loads(exec_resp.text)["result"])):
				print("Current status is: "+str(json.loads(exec_resp.text)["result"]))
				exec_resp=s.get(tormurl+"api/tjob/"+str(tjobId)+"/exec/"+str(json.loads(r.text)["id"]))
				time.sleep(5)
			print("Exit status is "+str(json.loads(exec_resp.text)["result"]))
			if "SUCCESS" in str(json.loads(exec_resp.text)["result"]):
				#print exec_resp.text
				print("TJob execution successful")
				return "success"
			else:
				#print exec_resp.text
				print("TJob execution failed")
				return "failed"
			
		except AssertionError:
			print("TJob execution failed")
			return "failed"
		
if __name__=="__main__":
	e2etests()	
