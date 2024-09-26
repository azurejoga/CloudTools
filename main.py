import os
import boto3
import json
from google.cloud import compute_v1
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient

# Carregar variáveis de ambiente
def load_env_variables():
    os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_AWS_ACCESS_KEY'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_AWS_SECRET_KEY'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_your_google_credentials.json'
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'YOUR_AZURE_SUBSCRIPTION_ID'
    os.environ['AZURE_RESOURCE_GROUP'] = 'YOUR_AZURE_RESOURCE_GROUP'

# Classe de Gerenciamento da AWS
class AWSManager:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.ec2 = self.login()
        self.cloudwatch = boto3.client('cloudwatch')
        self.cost_explorer = boto3.client('ce')

    def login(self):
        return boto3.client('ec2', region_name=self.region)

    def list_instances(self):
        return self.ec2.describe_instances()

    def start_instance(self, instance_id):
        self.ec2.start_instances(InstanceIds=[instance_id])

    def stop_instance(self, instance_id):
        self.ec2.stop_instances(InstanceIds=[instance_id])

    def create_instance(self, instance_type, ami_id):
        return self.ec2.run_instances(InstanceType=instance_type, ImageId=ami_id, MinCount=1, MaxCount=1)

    def get_cpu_utilization(self, instance_id):
        metrics = self.cloudwatch.get_metric_statistics(
            Period=300,
            StartTime='2023-09-01T00:00:00Z',
            EndTime='2023-09-01T01:00:00Z',
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Statistics=['Average'],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
        )
        return metrics['Datapoints']

    def monitor_costs(self):
        response = self.cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': '2023-09-01',
                'End': '2023-09-30'
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost']
        )
        return response

    def get_instance_status(self, instance_id):
        response = self.ec2.describe_instance_status(InstanceIds=[instance_id])
        return response['InstanceStatuses']

    def get_volume_info(self, instance_id):
        instance = self.ec2.describe_instances(InstanceIds=[instance_id])
        volumes = instance['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        return volumes

    def delete_instance(self, instance_id):
        self.ec2.terminate_instances(InstanceIds=[instance_id])

    def get_ram_usage(self, instance_id):
        try:
            memory_metrics = self.cloudwatch.get_metric_statistics(
                Period=300,
                StartTime='2023-09-01T00:00:00Z',
                EndTime='2023-09-01T01:00:00Z',
                MetricName='MemoryUtilization',
                Namespace='System/Linux',
                Statistics=['Average'],
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
            )
            return memory_metrics['Datapoints']
        except Exception as e:
            print(f"Erro ao obter uso de RAM: {e}")
            return None

    def get_storage_usage(self, instance_id):
        try:
            volumes = self.get_volume_info(instance_id)
            storage_usage = {}
            for volume in volumes:
                volume_id = volume['Ebs']['VolumeId']
                volume_details = self.ec2.describe_volumes(VolumeIds=[volume_id])
                storage_usage[volume_id] = volume_details['Volumes'][0]['Size']  # Size in GB
            return storage_usage
        except Exception as e:
            print(f"Erro ao obter uso de armazenamento: {e}")
            return None

# Classe de Gerenciamento do Google Cloud
class GoogleCloudManager:
    def __init__(self, project_id, zone):
        self.project_id = project_id
        self.zone = zone
        self.client = compute_v1.InstancesClient()

    def list_instances(self):
        return list(self.client.list(project=self.project_id, zone=self.zone))

    def create_instance(self, instance_name, machine_type, disk_size):
        disk = compute_v1.AttachedDisk()
        disk.initialize_params = compute_v1.AttachedDiskInitializeParams(
            source_image="projects/debian-cloud/global/images/family/debian-10",
            disk_size_gb=disk_size
        )
        disk.boot = True
        disk.auto_delete = True

        instance = compute_v1.Instance()
        instance.name = instance_name
        instance.zone = self.zone
        instance.machine_type = f"zones/{self.zone}/machineTypes/{machine_type}"
        instance.disks = [disk]
        operation = self.client.insert(self.project_id, self.zone, instance)
        operation.result()  # Aguarda a conclusão

    def get_ram_usage(self, instance_name):
        # Implementar lógica para obter uso de RAM via Stackdriver Monitoring ou API
        try:
            # Aqui você pode usar a API do Stackdriver Monitoring
            # Este exemplo é apenas um esboço e pode precisar de ajustes com base nas bibliotecas usadas
            # Utilize o MonitoringClient para obter métricas de RAM
            pass
        except Exception as e:
            print(f"Erro ao obter uso de RAM: {e}")

    def get_storage_usage(self, instance_name):
        # Implementar lógica para obter uso de armazenamento.
        try:
            instance = self.client.get(self.project_id, self.zone, instance_name)
            disks = instance.disks
            storage_usage = {disk.device_name: disk.disk_size_gb for disk in disks}
            return storage_usage
        except Exception as e:
            print(f"Erro ao obter uso de armazenamento: {e}")

    def delete_instance(self, instance_name):
        operation = self.client.delete(self.project_id, self.zone, instance_name)
        operation.result()  # Aguarda a conclusão

# Classe de Gerenciamento do Azure
class AzureManager:
    def __init__(self, subscription_id, resource_group):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.compute_client = ComputeManagementClient(DefaultAzureCredential(), self.subscription_id)
        self.network_client = NetworkManagementClient(DefaultAzureCredential(), self.subscription_id)

    def list_vms(self):
        return list(self.compute_client.virtual_machines.list(self.resource_group))

    def create_vm(self, vm_name, parameters):
        return self.compute_client.virtual_machines.begin_create_or_update(self.resource_group, vm_name, parameters)

    def get_vm_status(self, vm_name):
        instance = self.compute_client.virtual_machines.get(self.resource_group, vm_name)
        return instance.provisioning_state

    def delete_vm(self, vm_name):
        return self.compute_client.virtual_machines.begin_delete(self.resource_group, vm_name)

    def get_ram_usage(self, vm_name):
        # Utilize a API do Azure Monitor para obter uso de RAM.
        try:
            # Lógica para obter uso de RAM do Azure Monitor
            pass
        except Exception as e:
            print(f"Erro ao obter uso de RAM: {e}")

    def get_storage_usage(self, vm_name):
        # Implemente lógica para obter uso de armazenamento.
        try:
            instance = self.compute_client.virtual_machines.get(self.resource_group, vm_name)
            # Aqui você pode acessar as propriedades do disco
            # A lógica exata dependerá do formato de sua implementação
            return instance.storage_profile.os_disk.disk_size_gb
        except Exception as e:
            print(f"Erro ao obter uso de armazenamento: {e}")

# Menu Principal
def main_menu():
    load_env_variables()
    print("Bem-vindo ao Gerenciador de Nuvem!")
    while True:
        choice = input("Escolha uma nuvem para gerenciar (1: AWS, 2: Google Cloud, 3: Azure, 0: Sair): ")
        
        if choice == '1':
            aws_manager = AWSManager()
            aws_menu(aws_manager)
        elif choice == '2':
            google_manager = GoogleCloudManager('meu-projeto-google', 'us-central1-a')
            google_menu(google_manager)
        elif choice == '3':
            azure_manager = AzureManager(os.environ['AZURE_SUBSCRIPTION_ID'], os.environ['AZURE_RESOURCE_GROUP'])
            azure_menu(azure_manager)
        elif choice == '0':
            print("Saindo...")
            break
        else:
            print("Escolha inválida, tente novamente.")

def aws_menu(manager):
    while True:
        action = input("1: Listar, 2: Iniciar, 3: Parar, 4: Criar, 5: Monitorar CPU, 6: Monitorar Custos, 7: Status da Instância, 8: Uso de RAM, 9: Uso de Armazenamento, 10: Informações de Volume, 11: Deletar Instância, 0: Voltar: ")
        if action == '1':
            instances = manager.list_instances()
            print(instances)
        elif action == '2':
            instance_id = input("ID da Instância para iniciar: ")
            manager.start_instance(instance_id)
        elif action == '3':
            instance_id = input("ID da Instância para parar: ")
            manager.stop_instance(instance_id)
        elif action == '4':
            instance_type = input("Tipo da Instância: ")
            ami_id = input("ID da AMI: ")
            manager.create_instance(instance_type, ami_id)
        elif action == '5':
            instance_id = input("ID da Instância para monitorar CPU: ")
            print(manager.get_cpu_utilization(instance_id))
        elif action == '6':
            print(manager.monitor_costs())
        elif action == '7':
            instance_id = input("ID da Instância para obter status: ")
            print(manager.get_instance_status(instance_id))
        elif action == '8':
            instance_id = input("ID da Instância para obter uso de RAM: ")
            print(manager.get_ram_usage(instance_id))
        elif action == '9':
            instance_id = input("ID da Instância para obter uso de armazenamento: ")
            print(manager.get_storage_usage(instance_id))
        elif action == '10':
            instance_id = input("ID da Instância para obter informações de volume: ")
            print(manager.get_volume_info(instance_id))
        elif action == '11':
            instance_id = input("ID da Instância para deletar: ")
            manager.delete_instance(instance_id)
        elif action == '0':
            break
        else:
            print("Escolha inválida.")

def google_menu(manager):
    while True:
        action = input("1: Listar, 2: Criar, 3: Obter Uso de RAM, 4: Obter Uso de Armazenamento, 5: Deletar, 0: Voltar: ")
        if action == '1':
            instances = manager.list_instances()
            print(instances)
        elif action == '2':
            instance_name = input("Nome da Instância: ")
            machine_type = input("Tipo de Máquina: ")
            disk_size = input("Tamanho do Disco (GB): ")
            manager.create_instance(instance_name, machine_type, disk_size)
        elif action == '3':
            instance_name = input("Nome da Instância para obter uso de RAM: ")
            print(manager.get_ram_usage(instance_name))
        elif action == '4':
            instance_name = input("Nome da Instância para obter uso de armazenamento: ")
            print(manager.get_storage_usage(instance_name))
        elif action == '5':
            instance_name = input("Nome da Instância para deletar: ")
            manager.delete_instance(instance_name)
        elif action == '0':
            break
        else:
            print("Escolha inválida.")

def azure_menu(manager):
    while True:
        action = input("1: Listar VMs, 2: Criar VM, 3: Obter Status, 4: Deletar VM, 5: Obter Uso de RAM, 6: Obter Uso de Armazenamento, 0: Voltar: ")
        if action == '1':
            vms = manager.list_vms()
            print(vms)
        elif action == '2':
            vm_name = input("Nome da VM: ")
            parameters = {}  # Você pode preencher os parâmetros necessários
            manager.create_vm(vm_name, parameters)
        elif action == '3':
            vm_name = input("Nome da VM para obter status: ")
            print(manager.get_vm_status(vm_name))
        elif action == '4':
            vm_name = input("Nome da VM para deletar: ")
            manager.delete_vm(vm_name)
        elif action == '5':
            vm_name = input("Nome da VM para obter uso de RAM: ")
            print(manager.get_ram_usage(vm_name))
        elif action == '6':
            vm_name = input("Nome da VM para obter uso de armazenamento: ")
            print(manager.get_storage_usage(vm_name))
        elif action == '0':
            break
        else:
            print("Escolha inválida.")

if __name__ == "__main__":
    main_menu()
