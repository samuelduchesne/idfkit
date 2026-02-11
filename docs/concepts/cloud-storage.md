# Cloud & Remote Storage

idfkit's simulation module supports pluggable storage backends through the
`FileSystem` protocol, enabling cloud-native workflows with S3 and other
storage systems.

## The FileSystem Protocol

The `FileSystem` protocol defines a minimal interface for file operations:

```python
--8<-- "docs/snippets/concepts/cloud-storage/the_filesystem_protocol.py"
```

## Built-in Implementations

### LocalFileSystem

The default backend, wrapping `pathlib.Path` operations:

```python
--8<-- "docs/snippets/concepts/cloud-storage/localfilesystem.py"
```

### S3FileSystem

Amazon S3 backend for cloud workflows:

```python
--8<-- "docs/snippets/concepts/cloud-storage/s3filesystem.py"
```

Requires the `boto3` package: `pip install idfkit[s3]`

## Cloud Workflow Pattern

For cloud-based parametric simulations (AWS Batch, Kubernetes, etc.), the
typical workflow is:

### 1. Local Preparation

Create simulation jobs with S3 output paths:

```python
--8<-- "docs/snippets/concepts/cloud-storage/1_local_preparation.py"
```

### 2. Cloud Execution

Workers run simulations locally, results upload to S3:

```python
--8<-- "docs/snippets/concepts/cloud-storage/2_cloud_execution.py"
```

### 3. Result Collection

Retrieve results from S3 from any machine:

```python
--8<-- "docs/snippets/concepts/cloud-storage/3_result_collection.py"
```

## S3 Configuration

### Authentication

S3FileSystem uses boto3's credential chain:

1. Explicit credentials in constructor
2. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. IAM role (on EC2/ECS/Lambda)
4. Shared credentials file (`~/.aws/credentials`)

```python
--8<-- "docs/snippets/concepts/cloud-storage/authentication.py"
```

### S3-Compatible Services

Works with MinIO, LocalStack, and other S3-compatible services:

```python
--8<-- "docs/snippets/concepts/cloud-storage/s3_compatible_services.py"
```

### Key Prefixes

Use prefixes to namespace simulations:

```python
--8<-- "docs/snippets/concepts/cloud-storage/key_prefixes.py"
```

## Implementing Custom Backends

Implement the `FileSystem` protocol for other storage systems:

```python
--8<-- "docs/snippets/concepts/cloud-storage/implementing_custom_backends.py"
```

## EnergyPlus Execution

Important: **EnergyPlus always runs locally**. The FileSystem abstraction
covers:

- **Pre-simulation**: Preparing run directory
- **Post-simulation**: Uploading results
- **Result reading**: Downloading files on demand

The actual simulation happens in a local temporary directory, then results
are copied to the configured FileSystem.

## Performance Considerations

### Lazy Loading

Result files are read on-demand, so only accessed data is downloaded:

```python
--8<-- "docs/snippets/concepts/cloud-storage/lazy_loading.py"
```

### Local Caching

For repeated access, consider downloading to local disk:

```python
--8<-- "docs/snippets/concepts/cloud-storage/local_caching.py"
```

## See Also

- [Simulation Architecture](simulation-architecture.md) — Overall design
- [Caching Strategy](caching.md) — Local caching
- [Cloud Simulations Example](../examples/cloud-simulations.md) — Complete example
