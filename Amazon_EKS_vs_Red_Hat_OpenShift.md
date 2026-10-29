# Amazon EKS vs. Red Hat OpenShift

## A comparison for developers and DevOps teams

> **Scope:** This comparison covers Amazon Elastic Kubernetes Service (EKS), Red Hat OpenShift Container Platform (OCP), and Red Hat OpenShift Service on AWS (ROSA). ROSA is the closest like-for-like comparison with EKS because both are managed services on AWS. A self-managed OpenShift installation gives the customer more operational responsibility than ROSA.
>
> **Current as of:** October 2026. Product features, support boundaries, and prices change; verify them before making a purchasing decision.

## Executive summary

Both platforms run Kubernetes workloads and support standard objects such as Deployments, StatefulSets, Services, ConfigMaps, Secrets, Jobs, and PersistentVolumeClaims. A well-designed application container normally runs on either platform with limited manifest changes.

Their main difference is the platform boundary:

- **Amazon EKS** provides managed Kubernetes with close integration into AWS. Teams select and integrate many surrounding capabilities themselves. EKS Auto Mode reduces that work by managing compute, storage, load balancing, and parts of cluster networking.
- **Red Hat OpenShift** provides a more opinionated application platform built around Kubernetes. It adds integrated developer workflows, a developer-focused console, Routes, stronger default workload restrictions, Operators, platform monitoring, and coordinated lifecycle management.
- **ROSA** runs OpenShift on AWS with Red Hat operating much of the cluster platform. AWS describes ROSA as a managed OpenShift service, with Red Hat and the customer sharing specific responsibilities.

A short decision rule:

- Choose **EKS** when AWS-native integration, Kubernetes flexibility, and control over the platform toolchain matter most.
- Choose **OpenShift or ROSA** when a consistent, supported application platform and standardized developer experience matter more than selecting every component independently.
- Evaluate **EKS Auto Mode against ROSA**, rather than only comparing traditional EKS with OpenShift, when minimizing operational work is a primary goal.

## What is being compared?

### Amazon EKS

Amazon EKS is AWS's managed Kubernetes service. AWS operates the Kubernetes control plane. Customers run workloads on EKS Auto Mode managed nodes, managed node groups, self-managed EC2 nodes, AWS Fargate, or supported hybrid nodes. AWS documents the available compute choices in its [EKS compute guidance](https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html).

Traditional EKS deliberately leaves many platform choices to the customer. A platform team commonly selects and operates components for ingress, DNS, certificates, secrets integration, policy, observability, autoscaling, GitOps, and developer portals. AWS supplies managed add-ons for some components, while community and commercial tools cover others. See [Amazon EKS add-ons](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html).

[EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html) expands the managed boundary. It automates more of the node, block-storage, load-balancing, and compute-scaling lifecycle while keeping the Kubernetes API as the workload interface.

### Red Hat OpenShift

Red Hat OpenShift is an enterprise Kubernetes application platform. OpenShift Container Platform can run on AWS, other public clouds, virtualization platforms, bare metal, and disconnected infrastructure. It includes Kubernetes plus Red Hat-managed platform components and OpenShift-specific APIs and workflows.

OpenShift provides an integrated web console, the `oc` CLI, Operators, Routes, cluster monitoring, security defaults, image-management capabilities, and coordinated cluster updates. Its [architecture and development overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/architecture/understanding-development) describes the platform capabilities surrounding application development.

OpenShift is available in several operational models:

- **OpenShift Container Platform:** the customer installs and operates the platform.
- **ROSA:** Red Hat operates much of OpenShift on AWS. See [What is ROSA?](https://docs.aws.amazon.com/rosa/latest/userguide/what-is-rosa.html).
- **Other managed OpenShift offerings:** operational responsibilities vary by service and provider.

This distinction matters. Comparing EKS with self-managed OCP mixes a managed Kubernetes control plane with a customer-operated application platform. Comparing EKS or EKS Auto Mode with ROSA is more balanced.

## At-a-glance comparison

| Area | Amazon EKS | Red Hat OpenShift / ROSA |
|---|---|---|
| Core platform | Managed upstream-compatible Kubernetes on AWS | Enterprise Kubernetes distribution with additional platform APIs and integrated services |
| Primary cloud fit | AWS-first | Hybrid and multi-cloud; ROSA is AWS-specific |
| Control plane | Managed by AWS | Customer-managed in OCP; Red Hat-managed in ROSA |
| Worker infrastructure | Auto Mode, managed node groups, self-managed EC2, Fargate, or hybrid nodes | Customer-managed in OCP; responsibility is shared with Red Hat in ROSA |
| Developer CLI | `kubectl`, AWS CLI, and commonly `eksctl` | `oc`, which includes Kubernetes operations, plus `kubectl` compatibility |
| Developer console | AWS console exposes cluster and Kubernetes resources; teams often add separate developer tooling | Integrated administrator and developer web console with workload topology and catalog views |
| Application exposure | Kubernetes Service plus Ingress or Gateway implementation, commonly backed by ALB/NLB | Kubernetes Service plus OpenShift Route or Ingress; Route provides a direct platform convention |
| Container registry | Commonly Amazon ECR; registry is a separate AWS service | External registries supported; an integrated image registry can be deployed and managed by OpenShift |
| Image builds | Normally handled by CI/CD or external build services | External CI/CD works; OpenShift also supplies build and image-lifecycle APIs |
| CI/CD | Bring Azure DevOps, GitHub Actions, CodePipeline, GitLab, Argo CD, Flux, or another system | External systems work; OpenShift Pipelines and OpenShift GitOps can be installed as supported Operators |
| User identity | AWS IAM mapped through EKS access entries, then Kubernetes authorization | Configured identity provider and OAuth plus Kubernetes RBAC; ROSA also uses AWS identities for service-level integration |
| Workload AWS identity | EKS Pod Identity or IAM Roles for Service Accounts | AWS workload identity patterns depend on the OpenShift/ROSA setup and installed operators |
| Default workload security | Standard Kubernetes controls; the platform team chooses and enforces admission policy | Restricted SCC defaults strongly influence container design, including arbitrary non-root UIDs |
| Networking | Amazon VPC CNI by default; AWS load balancer and network integrations | OVN-Kubernetes is the usual default; OpenShift Ingress Operator and Routes provide platform conventions |
| Monitoring | Assemble from CloudWatch, Managed Service for Prometheus, ADOT, third-party tools, or self-managed stacks | Platform monitoring is integrated; user-workload monitoring can be enabled and configured separately |
| Add-on model | EKS managed add-ons, Helm, GitOps, AWS Marketplace, and community projects | Cluster Operators plus Operator Lifecycle Manager and OperatorHub; Helm and GitOps also work |
| Upgrade model | AWS upgrades the control plane when initiated; customers coordinate data plane and add-ons unless covered by a managed option | Cluster Version Operator coordinates supported platform updates; customer schedules OCP updates, while ROSA responsibilities are shared with Red Hat |
| Portability | Standard Kubernetes resources are portable; AWS controllers and IAM integrations create AWS coupling | Standard resources are portable; Routes, SCCs, ImageStreams, Builds, and other OpenShift APIs create OpenShift coupling |
| Support model | AWS supports EKS and AWS-managed components; responsibility for selected third-party components remains with the customer or vendor | Red Hat supports the integrated OpenShift distribution; ROSA support spans AWS and Red Hat responsibility boundaries |
| Cost model | EKS cluster charge plus compute, storage, networking, observability, support, and optional extended-support or Auto Mode charges | OCP subscription plus infrastructure and operations, or ROSA service fees plus AWS infrastructure and support |

## Developer perspective

### 1. Getting an application deployed

On either platform, a developer can apply a standard Deployment and Service:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

OpenShift developers commonly use `oc`, although `kubectl` remains usable for standard Kubernetes resources:

```bash
oc apply -f deployment.yaml
oc apply -f service.yaml
oc expose service taskboard
```

The final command creates an OpenShift Route. On EKS, exposing the same service externally usually requires an Ingress or Gateway resource and a configured controller, or a `LoadBalancer` Service. The platform team must establish which controller, annotations, DNS process, and certificate process developers should use. With OpenShift, the Route and Ingress Operator provide a more uniform built-in convention.

**Developer effect:** OpenShift usually offers a shorter standardized path from Service to URL. EKS offers more freedom over the ingress implementation and closer control of AWS ALB/NLB behavior.

### 2. Developer portal and self-service

OpenShift includes a developer perspective in its web console. Depending on installed Operators and administrator configuration, developers can inspect topology, logs, builds, Routes, metrics, and catalog content without moving among several products.

The AWS console shows EKS clusters and Kubernetes resources, but EKS does not prescribe a complete developer portal. Organizations commonly combine it with internal templates, Backstage, GitOps repositories, dashboards, and AWS services.

**Developer effect:** OpenShift gives teams a consistent interface sooner. EKS allows a company to build a portal and workflow around its preferred tools, but that platform-engineering work belongs to the company.

### 3. Building container images

EKS normally separates image building from the cluster. A CI system builds an image, pushes it to ECR or another registry, and deploys its immutable tag or digest to EKS.

OpenShift supports that same external CI workflow. It can also provide an internal image registry and cluster build APIs. Red Hat describes the integrated registry and image lifecycle in the [OpenShift image registry overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/registry/registry-overview). The registry is a platform capability, but administrators still have to configure durable backing storage and decide whether developers may expose or use it directly.

**Developer effect:** EKS reinforces an external CI-and-registry model. OpenShift supports that model while also offering cluster-native build and image-management options.

### 4. Application configuration and secrets

Both platforms use Kubernetes ConfigMaps and Secrets. In both cases, a Kubernetes Secret is not automatically a complete enterprise secrets-management solution.

EKS teams frequently integrate AWS Secrets Manager or Systems Manager Parameter Store through a CSI driver, external-secrets controller, or application SDK. Workloads can receive temporary AWS credentials through EKS Pod Identity. AWS explains the credential mechanism in [How EKS Pod Identity works](https://docs.aws.amazon.com/eks/latest/userguide/pod-id-how-it-works.html).

OpenShift teams can use Kubernetes Secrets, external secret stores, CSI integrations, Vault, or cloud-provider services. OpenShift provides common RBAC and operator-based deployment patterns across infrastructures.

**Developer effect:** EKS provides a particularly direct path to AWS APIs. OpenShift provides a more uniform pattern when applications must run across different infrastructures.

### 5. Container security compatibility

OpenShift normally starts application containers with an arbitrary non-root UID under a restricted Security Context Constraint. New pods use restrictive defaults such as `restricted-v2`, as documented in Red Hat's [seccomp and restricted SCC guidance](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/security_and_compliance/seccomp-profiles).

A portable image should therefore:

- Avoid requiring UID 0.
- Avoid assuming a fixed numeric UID.
- Make writable paths compatible with the assigned runtime user and group.
- Avoid writing into the application image filesystem.
- Declare state through mounted volumes.

EKS can enforce similarly strict policies, but Kubernetes and EKS do not automatically make every cluster follow the same OpenShift SCC model. The EKS platform team chooses Pod Security Admission settings and any additional policy engine.

**Developer effect:** An image that works on a permissive EKS namespace might fail under OpenShift's defaults. An image designed for OpenShift's arbitrary-UID model generally has a good security baseline for either platform.

### 6. Portability of manifests

The following objects normally transfer with few changes:

- Deployment
- StatefulSet
- DaemonSet
- Service
- ConfigMap
- Secret
- Job and CronJob
- PersistentVolumeClaim, subject to available storage classes
- HorizontalPodAutoscaler, subject to metrics availability

Common changes when moving between the platforms include:

| EKS-oriented resource or setting | OpenShift-oriented equivalent or consideration |
|---|---|
| ALB/NLB annotations | OpenShift Route, Ingress, or provider-specific service configuration |
| ACM certificate reference | Route TLS or a configured certificate-management solution |
| EKS Pod Identity association | OpenShift/ROSA workload identity or external-secret integration |
| EBS/EFS storage class | StorageClass supplied by the OpenShift installation |
| AWS-specific controller CRD | Corresponding OpenShift Operator or infrastructure-neutral API |
| Pod running under a fixed UID | Arbitrary-UID-compatible image and security context |
| Standard Ingress | Route or Ingress, depending on platform convention |

Using only standard Kubernetes APIs improves portability, but it can also prevent a team from using valuable platform features. The practical goal should be controlled platform-specific overlays rather than pretending that every production deployment is identical.

## DevOps and platform-engineering perspective

### 1. Operational responsibility

AWS operates the EKS Kubernetes control plane. In traditional EKS, the customer remains responsible for many data-plane and add-on decisions. AWS's [EKS security responsibility guidance](https://docs.aws.amazon.com/eks/latest/userguide/security.html) identifies the control plane as an AWS responsibility, while the exact customer burden varies with the selected compute and add-on model.

EKS Auto Mode moves more compute, storage, and load-balancing work into the managed service boundary. It should be assessed separately from managed node groups or self-managed nodes.

With self-managed OpenShift Container Platform, the customer operates both the infrastructure and the OpenShift platform. That includes cluster Operators, upgrades, capacity, ingress, storage integration, monitoring configuration, certificates, and platform recovery.

With ROSA, Red Hat operates much of the underlying application platform while the customer remains responsible for applications, workloads, data, access decisions, and agreed infrastructure areas. AWS publishes an explicit [ROSA responsibilities matrix](https://docs.aws.amazon.com/rosa/latest/userguide/rosa-responsibilities.html).

**DevOps effect:** Traditional EKS requires more platform assembly. Self-managed OCP requires broader cluster operations. EKS Auto Mode and ROSA reduce different portions of the operational burden.

### 2. Platform composition versus platform standardization

EKS encourages composability. A platform team can choose:

- Ingress and Gateway controllers
- Autoscalers
- Policy engines
- Service mesh
- Secrets integration
- Monitoring and logging stacks
- GitOps controllers
- Developer portal
- Backup and disaster-recovery products

This allows precise alignment with existing AWS standards. It also creates an integration and lifecycle matrix that the platform team must own.

OpenShift delivers a tested core platform with coordinated Operators and APIs. Optional capabilities, such as OpenShift GitOps, OpenShift Pipelines, service mesh, and external secret solutions, still require selection and operation, but the supported installation path is usually more standardized.

**DevOps effect:** EKS favors choice and AWS service composition. OpenShift favors consistency, supportability, and repeatable platform conventions.

### 3. Identity and access management

EKS access begins with AWS IAM. AWS recommends EKS access entries for associating IAM identities with Kubernetes permissions; see [EKS access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html). Kubernetes RBAC still determines or contributes to what authenticated users may do inside the cluster.

OpenShift has an OAuth layer that integrates configured identity providers with Kubernetes users, groups, and RBAC. ROSA also depends on AWS IAM and STS for service provisioning and platform integration, while cluster-user authentication can use a configured identity provider.

**DevOps effect:** EKS aligns naturally with an established AWS Organizations and IAM operating model. OpenShift provides a consistent cluster identity experience across clouds, but ROSA administrators must understand both the AWS and OpenShift identity layers.

### 4. Workload access to cloud services

EKS Pod Identity associates a Kubernetes service account with an IAM role and supplies temporary credentials to compatible workloads. This offers a native AWS pattern without storing long-lived keys in Kubernetes Secrets.

OpenShift on AWS can also use temporary AWS identities, but the implementation and support path depend on whether the cluster is OCP or ROSA and on the selected Operators. On non-AWS OpenShift clusters, equivalent integrations depend on the infrastructure provider.

**DevOps effect:** EKS is usually simpler for applications that make extensive use of AWS APIs. OpenShift is more consistent for organizations that value one application-platform model across AWS, other clouds, and on-premises systems.

### 5. Networking and load balancing

EKS commonly uses the Amazon VPC CNI, which assigns VPC networking to pods. AWS documents its role in [Amazon VPC CNI networking](https://docs.aws.amazon.com/eks/latest/userguide/cni-iam-role.html). External traffic commonly uses the AWS Load Balancer Controller or EKS Auto Mode load-balancing capability. The organization controls VPC design, address consumption, security groups, private endpoints, and controller configuration.

OpenShift commonly uses OVN-Kubernetes and an Ingress Operator. Routes give teams a stable OpenShift API for exposing HTTP and TLS services. The platform team manages the relationship among Routes, wildcard DNS, router certificates, ingress controllers, and external load balancers.

**DevOps effect:** EKS exposes AWS networking constructs more directly. OpenShift places a stronger platform abstraction in front of ingress, though administrators still need to design the underlying AWS network correctly.

### 6. Observability

EKS can use CloudWatch Container Insights, Amazon Managed Service for Prometheus, Amazon Managed Grafana, AWS Distro for OpenTelemetry, or third-party and self-managed stacks. This makes integration with an existing AWS observability environment straightforward, but the platform team must define the reference architecture.

OpenShift includes platform monitoring based on Prometheus and Alertmanager and integrates it into the console. Monitoring of application namespaces is separately configurable. Red Hat documents this in [user-workload monitoring](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/monitoring/configuring-user-workload-monitoring).

**DevOps effect:** OpenShift supplies a common operational starting point. EKS provides broad AWS-native options and lets teams decide how much to standardize.

### 7. Upgrades and lifecycle management

For EKS, the team chooses when to upgrade the control plane within the supported version policy and must coordinate compatible node images, managed node groups, Fargate behavior, controllers, add-ons, APIs, and application disruption budgets. Managed add-ons and Auto Mode reduce parts of that work but do not remove application compatibility testing.

OpenShift uses release payloads and the Cluster Version Operator to coordinate supported component updates. The available update graph avoids unsupported version jumps; see [Understanding OpenShift updates](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/updating_clusters/understanding-openshift-updates-1). The customer still plans maintenance, validates workloads, monitors the update, and handles blocked or degraded Operators. In ROSA, Red Hat takes on more platform maintenance under the service's responsibility model.

**DevOps effect:** OpenShift has a more unified platform update mechanism. EKS gives teams more independent control of components, at the cost of more compatibility coordination.

### 8. Security and policy

Both platforms support Kubernetes RBAC, NetworkPolicy, security contexts, audit logs, admission controls, image scanning integrations, and external policy engines.

EKS integrates closely with IAM, KMS, CloudTrail, Security Hub, GuardDuty, VPC controls, and AWS security services. Kubernetes NetworkPolicy support depends on the configured networking capabilities; AWS documents the default-open behavior and policy setup in [EKS network policy guidance](https://docs.aws.amazon.com/eks/latest/userguide/cni-network-policy.html).

OpenShift adds Security Context Constraints and provides restrictive workload defaults. This reduces the chance that application teams accidentally depend on privileged execution, but it can increase initial migration work for older images.

**DevOps effect:** EKS fits naturally into AWS security governance. OpenShift starts with more application-platform guardrails and supplies a consistent policy model across infrastructures.

### 9. Support and troubleshooting

With EKS, AWS supports the managed service and AWS components. Support for a self-installed ingress controller, service mesh, policy engine, observability stack, or GitOps controller may come from its vendor or community. Platform teams need a clear ownership map to avoid gaps between components.

With OpenShift, Red Hat supports the tested platform distribution and its supported Operators. Third-party applications and unsupported customizations remain outside that boundary. With ROSA, incidents can span AWS infrastructure and Red Hat platform responsibilities, so the published responsibility matrix and support process are important.

**DevOps effect:** OpenShift can reduce the number of support boundaries for the core platform. EKS can be simpler when the organization already standardizes on AWS-native services and accepts responsibility for the selected Kubernetes ecosystem components.

## CI/CD comparison using Azure DevOps

Azure DevOps can deploy to either platform.

### Typical EKS pipeline

```text
Azure Repos or GitHub
  → Azure DevOps agent builds the image
  → push to Amazon ECR
  → authenticate to AWS
  → update kubeconfig or use a controlled deployment identity
  → kubectl/Helm/GitOps deploys to EKS
  → verify rollout
```

The agent needs AWS permissions for ECR and an IAM identity authorized through EKS access entries. For production, prefer temporary federated credentials over stored long-lived access keys.

### Typical OpenShift pipeline

```text
Azure Repos or GitHub
  → Azure DevOps agent builds the image
  → push to an approved registry
  → authenticate with a namespace-scoped OpenShift identity
  → oc/kubectl/Helm/GitOps deploys to OpenShift
  → verify rollout
```

The agent needs network access to the OpenShift API and permission in the target project. A namespace-scoped service account is suitable for a classroom demonstration; a production pipeline should receive only the verbs and resources it needs.

### Shared recommendation

In both environments:

- Build the image once.
- Tag it with an immutable build identifier.
- Record and preferably deploy its digest.
- Keep credentials outside pipeline YAML.
- Separate build identity from deployment identity.
- Require approval when promoting to controlled environments.
- Verify readiness and rollout status before declaring success.
- Keep application data outside the container image.

## Mapping the TaskBoard exercises to EKS

The course's TaskBoard application illustrates which concepts transfer directly and which need platform-specific treatment.

| Course operation on OpenShift | EKS equivalent |
|---|---|
| Apply a Deployment | Apply the same Kubernetes Deployment, after checking its security context and image reference |
| Request a `ReadWriteOnce` PVC | Use an EBS-backed StorageClass and EBS CSI capability, or an appropriate Auto Mode storage class |
| Create a Service | Apply the same Kubernetes Service |
| Create an OpenShift Route | Create an Ingress/Gateway or `LoadBalancer` Service using the selected AWS controller |
| Use the cluster wildcard TLS certificate | Configure ACM and the load balancer/controller, or install a certificate-management solution |
| Link an image pull secret | For private ECR, configure appropriate node/runtime access; other private registries may still require an image pull Secret |
| Use an arbitrary OpenShift UID | Set and enforce an appropriate non-root security context and admission policy on EKS |
| Run `oc adm top pods` | Run `kubectl top pods` after Metrics Server or the selected metrics path is available |
| Use OpenShift console Observe pages | Use the selected AWS or third-party observability dashboards |
| Deploy through `oc set image` | Use `kubectl set image`, Helm, Kustomize, or GitOps |
| Create ConfigMaps and Secrets | Use the same Kubernetes APIs; optionally integrate AWS Secrets Manager |
| Roll back a Deployment | Use Kubernetes rollout history/undo or revert through GitOps |

The application's state limitation is identical on both platforms. A single JSON file on a `ReadWriteOnce` volume is not safe for horizontal scaling. Moving state into a database is an application architecture requirement, not an EKS or OpenShift feature difference.

## Cost considerations

Do not compare only the visible cluster fee. Compare the total platform cost:

- Control-plane or cluster service fees
- Worker compute
- Persistent storage and snapshots
- Load balancers, NAT gateways, and network transfer
- Registry storage and transfer
- Logging and metrics ingestion and retention
- Backup and disaster recovery
- Security and policy products
- Support plans and subscriptions
- Platform-engineering and on-call labor
- Upgrade, integration, and compliance work

EKS generally has a lower platform subscription layer, but a production platform may require additional services and engineering. OpenShift or ROSA carries a larger platform/service charge, but some capabilities and support are bundled into a standardized platform.

Use the current official [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/) and [ROSA pricing](https://aws.amazon.com/rosa/pricing/) pages. For self-managed OCP, request subscription pricing and include the infrastructure and staff required to operate it. Do not assume that the lowest hourly cluster charge produces the lowest total operating cost.

## When EKS is usually the better fit

EKS is a strong fit when:

- The organization is committed primarily to AWS.
- Applications use many AWS services directly.
- The platform team has strong Kubernetes and AWS expertise.
- The organization wants to choose its own ingress, policy, observability, and delivery stack.
- Existing governance is centered on AWS IAM, Organizations, Control Tower, CloudTrail, KMS, and related services.
- Avoiding OpenShift-specific APIs is a priority.
- EKS Auto Mode provides enough operational automation for the target workloads.
- The organization accepts responsibility for integrating and supporting the selected add-ons.

## When OpenShift or ROSA is usually the better fit

OpenShift or ROSA is a strong fit when:

- Developers need a standardized self-service application platform.
- The organization wants the same platform conventions across AWS, other clouds, and on-premises systems.
- A developer console, Routes, Operators, integrated monitoring, and restrictive defaults are valuable.
- Red Hat support for an integrated platform is important.
- The organization prefers coordinated lifecycle management over assembling independent Kubernetes components.
- Existing applications or teams already use OpenShift APIs and workflows.
- The business wants Red Hat to operate much of the OpenShift platform through ROSA.
- Disconnected or tightly controlled deployment patterns are required.

## Questions for a proof of concept

Before choosing a platform, test representative workloads and answer:

### Developer experience

- How does a new developer receive namespace access?
- How many steps take an application from source code to a TLS URL?
- Can a developer diagnose a failed rollout without administrator privileges?
- Which platform-specific manifest changes are required?
- Do existing images run as non-root and under arbitrary UIDs?
- How are local development, CI, and production kept consistent?

### Platform operations

- Who owns ingress, DNS, certificates, storage drivers, autoscaling, policy, logging, and monitoring?
- Who patches worker operating systems and cluster add-ons?
- What is the tested upgrade and rollback procedure?
- How are temporary cloud credentials issued to workloads and pipelines?
- What is the support path when an incident crosses the cloud, Kubernetes, and add-on boundaries?
- What cluster recovery and application backup objectives can be demonstrated?

### Cost and organization

- What does each option cost at the expected steady-state and peak capacity?
- How much platform-engineering labor is required?
- Are existing AWS or Red Hat enterprise agreements relevant?
- Does the company optimize for AWS specialization or cross-environment consistency?
- Which option better matches the skills of the teams that will operate it at 03:00?

## Practical conclusion

EKS and OpenShift share Kubernetes at the workload layer, but they offer different platform contracts.

EKS gives DevOps teams an AWS-native Kubernetes foundation and substantial freedom over the surrounding stack. That freedom can lower licensing cost and improve alignment with AWS services, but the organization must design, integrate, secure, upgrade, and support more of the application platform. EKS Auto Mode narrows this operational gap and should be included in any current evaluation.

OpenShift gives developers and operators a more standardized platform with stronger built-in conventions. It generally reduces tool-selection and integration work, while introducing OpenShift-specific APIs, stricter image requirements, subscription costs, and a broader platform lifecycle. ROSA moves much of that lifecycle to Red Hat while retaining the OpenShift developer model on AWS.

The choice should therefore be based less on whether both can run a Kubernetes Deployment—they can—and more on which organization should own the platform decisions around that Deployment.

## Official references

### AWS

- [Amazon EKS documentation](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
- [EKS compute options](https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html)
- [EKS add-ons](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html)
- [EKS access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html)
- [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-id-how-it-works.html)
- [Security in Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/security.html)
- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/)

### Red Hat OpenShift and ROSA

- [OpenShift Container Platform documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20)
- [OpenShift development architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/architecture/understanding-development)
- [OpenShift image registry](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/registry/registry-overview)
- [OpenShift user-workload monitoring](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/monitoring/configuring-user-workload-monitoring)
- [OpenShift security and restricted SCC defaults](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/security_and_compliance/seccomp-profiles)
- [OpenShift update architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/updating_clusters/understanding-openshift-updates-1)
- [What is ROSA?](https://docs.aws.amazon.com/rosa/latest/userguide/what-is-rosa.html)
- [ROSA responsibilities](https://docs.aws.amazon.com/rosa/latest/userguide/rosa-responsibilities.html)
- [ROSA pricing](https://aws.amazon.com/rosa/pricing/)

*Content based on external documentation was rephrased for compliance with licensing restrictions.*
