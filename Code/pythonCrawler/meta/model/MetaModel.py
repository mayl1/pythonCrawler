from django.db import models
class MetaInfo(models.Model):
    # id
    metaId = models.BigAutoField(primary_key=True, db_column="META_ID", max_length=12)
    metaName = models.CharField(db_column="META_NAME", max_length=256)

    metaCode = models.CharField(db_column="META_CODE", max_length=32)

    metaUrl = models.CharField(db_column="META_URL", max_length=1024)

    metaActor = models.CharField(db_column="META_ACTOR", max_length=512)

    metaDirector = models.CharField(db_column="META_DIRECTOR", max_length=128)

    metaPicture = models.CharField(db_column="META_PICTURE", max_length=256)

    metaSource = models.CharField(db_column="META_SORUCE", max_length=2)


    class Meta:
        db_table = "META_INFO"



