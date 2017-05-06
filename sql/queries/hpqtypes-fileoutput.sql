SELECT batch.id
     , result.id
     , fout.file_extension
     , fout.file_size
  FROM thesis.package as package
    INNER JOIN thesis.batch as batch ON batch.package = package.id
    INNER JOIN thesis.result as result ON batch.id = result.batch
    INNER JOIN thesis.file_output as fout ON fout.result = result.id
  WHERE package.name = 'hpqtypes'
    AND fout.file_size > 10000000;
