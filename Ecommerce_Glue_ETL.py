import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.gluetypes import *
from awsglue.dynamicframe import DynamicFrame
from awsglue import DynamicFrame
from pyspark.sql import functions as SqlFuncs

def _find_null_fields(ctx, schema, path, output, nullStringSet, nullIntegerSet, frame):
    if isinstance(schema, StructType):
        for field in schema:
            new_path = path + "." if path != "" else path
            output = _find_null_fields(ctx, field.dataType, new_path + field.name, output, nullStringSet, nullIntegerSet, frame)
    elif isinstance(schema, ArrayType):
        if isinstance(schema.elementType, StructType):
            output = _find_null_fields(ctx, schema.elementType, path, output, nullStringSet, nullIntegerSet, frame)
    elif isinstance(schema, NullType):
        output.append(path)
    else:
        x, distinct_set = frame.toDF(), set()
        for i in x.select(path).distinct().collect():
            distinct_ = i[path.split('.')[-1]]
            if isinstance(distinct_, list):
                distinct_set |= set([item.strip() if isinstance(item, str) else item for item in distinct_])
            elif isinstance(distinct_, str) :
                distinct_set.add(distinct_.strip())
            else:
                distinct_set.add(distinct_)
        if isinstance(schema, StringType):
            if distinct_set.issubset(nullStringSet):
                output.append(path)
        elif isinstance(schema, IntegerType) or isinstance(schema, LongType) or isinstance(schema, DoubleType):
            if distinct_set.issubset(nullIntegerSet):
                output.append(path)
    return output

def drop_nulls(glueContext, frame, nullStringSet, nullIntegerSet, transformation_ctx) -> DynamicFrame:
    nullColumns = _find_null_fields(frame.glue_ctx, frame.schema(), "", [], nullStringSet, nullIntegerSet, frame)
    return DropFields.apply(frame=frame, paths=nullColumns, transformation_ctx=transformation_ctx)

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node MySQL
MySQL_node1718909704268 = glueContext.create_dynamic_frame.from_options(
    connection_type = "mysql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "Transactions",
        "connectionName": "Mysql connection",
    },
    transformation_ctx = "MySQL_node1718909704268"
)

# Script generated for node Drop Duplicates
DropDuplicates_node1718909732008 =  DynamicFrame.fromDF(MySQL_node1718909704268.toDF().dropDuplicates(), glueContext, "DropDuplicates_node1718909732008")

# Script generated for node Drop Fields
DropFields_node1718909733798 = DropFields.apply(frame=DropDuplicates_node1718909732008, paths=[], transformation_ctx="DropFields_node1718909733798")

# Script generated for node Drop Null Fields
DropNullFields_node1718909735622 = drop_nulls(glueContext, frame=DropFields_node1718909733798, nullStringSet={""}, nullIntegerSet={}, transformation_ctx="DropNullFields_node1718909735622")

# Script generated for node Change Schema
ChangeSchema_node1718910058070 = ApplyMapping.apply(frame=DropNullFields_node1718909735622, mappings=[("transaction_id", "bigint", "transaction_id", "bigint"), ("customer_id", "int", "customer_id", "int"), ("name", "string", "name", "string"), ("email", "string", "email", "string"), ("phone", "string", "phone", "string"), ("address", "string", "address", "string"), ("city", "string", "city", "string"), ("state", "string", "state", "string"), ("zipcode", "int", "zipcode", "int"), ("country", "string", "country", "string"), ("age", "int", "age", "int"), ("gender", "string", "gender", "string"), ("income", "string", "income", "string"), ("customer_segment", "string", "customer_segment", "string"), ("date", "string", "date", "string"), ("year", "int", "year", "int"), ("month", "string", "month", "string"), ("time", "timestamp", "time", "timestamp"), ("total_purchases", "int", "total_purchases", "int"), ("amount", "decimal", "amount", "decimal"), ("total_amount", "decimal", "total_amount", "decimal"), ("product_category", "string", "product_category", "string"), ("product_brand", "string", "product_brand", "string"), ("product_type", "string", "product_type", "string"), ("feedback", "string", "feedback", "string"), ("shipping_method", "string", "shipping_method", "string"), ("payment_method", "string", "payment_method", "string"), ("order_status", "string", "order_status", "string"), ("ratings", "int", "ratings", "int"), ("products", "string", "products", "string")], transformation_ctx="ChangeSchema_node1718910058070")

# Script generated for node SQL Query
SqlQuery0 = '''
WITH calculated AS (
    SELECT *,
        CASE
            WHEN Total_Amount IS NULL THEN 
                COALESCE(Total_Purchases * COALESCE(Amount, 0), 0)
            ELSE 
                Total_Amount
        END AS Total_Amount_Calculated
    FROM myDataSource
)
SELECT *,
    CASE
        WHEN Total_Amount_Calculated < 170 THEN 'Silver'
        WHEN Total_Amount_Calculated >= 170 AND Total_Amount_Calculated <= 1200 THEN 'Gold'
        ELSE 'Platinum'
    END AS Purchase_Category
FROM calculated;
'''
SQLQuery_node1718914529113 = sparkSqlQuery(glueContext, query = SqlQuery0, mapping = {"myDataSource":ChangeSchema_node10058070}, transformation_ctx = "SQLQuery_node171529113")

# Script generated for node Amazon S3
AmazonS3_node1718909970768 = glueContext.write_dynamic_frame.from_options(frame=SQLQuery_node1718914529113, connection_type="s3", format="csv", connection_options={"path": "s3://datalakeecomm", "partitionKeys": []}, transformation_ctx="AmazonS3_node171890768")

job.commit()