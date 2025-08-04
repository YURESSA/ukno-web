<template>
  <div class="requesits-wrapper">
    <h5>Реквизиты организации</h5>

    <p>Свердловская областная общественная организация «Уральский клуб нового образования» (сокращенное наименование — УКНО)</p>

    <div class="text-wrapper">
      <h5>Банковские реквизиты:</h5>
      <p>
        р/с N° 40703810802500002872 <br>
        в ООО «БАНК ТОЧКА» г. Москва <br>
        БИК 044525104 <br>
        к/с 30101810745374525104 <br>
      </p>
    </div>

    <div class="text-wrapper">
      <h5>Юридический адрес:</h5>
      <p>
        620091, г. Екатеринбург, <br>
        проспект Космонавтов, 52а, помещение 10 <br>
        ИНН 6662022920 КПП 668601001 <br>
        ОГРН 1036605606135 <br>
      </p>
    </div>
  </div>
</template>

<style lang="css" scoped>
.requesits-wrapper{
  display: flex;
  flex-direction: column;
  align-items: left;
  border-radius: 26px;
  width: 819px;
  box-shadow: 0 0 13px 0 rgba(0, 0, 0, 0.18);
  margin: 0 auto;
  margin-top: 210px;
  margin-bottom: 100px;
  padding: 80px 40px;
}

.requesits-wrapper > h5 {
  font-family: 'Manrope', Arial, Helvetica, sans-serif;
  margin-bottom: 20px;
}

.text-wrapper{
  margin-top: 40px;
}

.text-wrapper > h5{
  font-size: 20px;
  font-family: 'Manrope', Arial, Helvetica, sans-serif;
}
</style>
