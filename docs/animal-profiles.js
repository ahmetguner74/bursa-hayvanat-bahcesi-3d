const penguinBehaviors={
  'Bakınıyor':'Başını çevirerek çevresini ve kolonisindeki diğer penguenleri izliyor.',
  'Silkeleniyor':'Gövdesini kısa bir hareketle silkeleyip yeniden sakinleşiyor.',
  'Tüylerini düzeltiyor':'Gagasıyla tüylerine bakım yapıyor. Sık tüyleri suda kuru ve sıcak kalmasına yardımcı olur.',
  'Uykuya hazırlanıyor':'Önce çömeliyor, ardından dinlenme pozisyonuna geçiyor.',
  'Uyuyor':'Kıyıda sakin bir uyku molası veriyor.',
  'Uyanıyor':'Yavaşça doğrulup yeniden çevresini izlemeye hazırlanıyor.',
  'Yüzüyor':'Kanatlarını yüzgeç gibi kullanarak havuzda kısa bir tur atıyor.',
  'Suda dinleniyor':'Yüzeyde sakin biçimde durup bir sonraki hareketinden önce dinleniyor.',
  'Dinleniyor':'Hareketleri arasında kısa bir mola veriyor.',
};

/** Species facts and descriptions; behavior always comes from the observed rig. */
export const ANIMAL_PROFILES={
  penguin:{
    name:'Afrika pengueni',scientific:'Spheniscus demersus',back:'Koloniye dön',backLabel:'Penguen kolonisine dön',
    summary:'Kayalık kıyılarda yaşar, iyi bir yüzücüdür.',
    description:"Güney Afrika ve Namibya'nın kayalık kıyılarında koloniler halinde yaşar. Uçamaz; suda çok iyi yüzer ve balıklarla beslenir.",
    facts:[['Boy','61–69 cm'],['Yaşam','Kıyı ve deniz']],source:'https://animals.sandiegozoo.org/animals/african-penguin',
    rest:['Dinleniyor',penguinBehaviors.Dinleniyor],behaviors:penguinBehaviors,
  },
  rhino:{
    name:'Beyaz gergedan',scientific:'Ceratotherium simum',back:'Sürüye dön',backLabel:'Gergedan sürüsüne dön',
    summary:'Otlaklarda yaşar, otlarla beslenir.',
    description:'Afrika’nın otlaklarında yaşar. Geniş dudakları otları toplamaya uygundur. Adındaki “beyaz” rengi belirtmez; derisi gri tonlarındadır.',
    facts:[['Beslenme','Otlar'],['Yaşam','Otlaklar']],source:'https://animals.sandiegozoo.org/animals/rhinoceros',
    rest:['Dinleniyor','Hareketleri arasında sakin biçimde duruyor.'],
    behaviors:{Look:['Bakınıyor','Başını hafifçe çevirerek çevresini izliyor.'],Ears:['Kulaklarını oynatıyor','Kulaklarını küçük hareketlerle farklı yönlere çeviriyor.'],walk:['Yürüyor','Yaşam alanında ağır ve dengeli adımlarla kısa bir yürüyüş yapıyor.']},
  },
  giraffe:{
    name:'Zürafa',scientific:'Giraffa camelopardalis',back:'Sürüye dön',backLabel:'Zürafa sürüsüne dön',
    summary:'Yüksek dallardaki yapraklarla beslenir.',
    description:'Afrika’nın ağaçlı savannalarında yaşar. Uzun boynu sayesinde yüksek dallardaki yapraklara ulaşır. Ayakta da dinlenebilir.',
    facts:[['Beslenme','Yapraklar'],['Yaşam','Savanna']],source:'https://animals.sandiegozoo.org/animals/giraffe',
    rest:['Dinleniyor','Ayakta sakin biçimde durup çevresini gözlüyor.'],
    behaviors:{Idle_Source_BlueMesh:['Çevresini izliyor','Boynunu ve başını hafifçe hareket ettirerek çevresine bakıyor.'],walk:['Yürüyor','Uzun bacaklarıyla sakin adımlar atarak yaşam alanında ilerliyor.']},
  },
  aviary:{
    name:'Flamingo',scientific:'Phoenicopterus roseus',back:'Koloniye dön',backLabel:'Flamingo kolonisine dön',
    summary:'Sığ sularda, koloniler halinde yaşar.',
    description:'Sığ göller ve lagünlerde koloniler halinde yaşar. Uzun bacakları suda dolaşmasını, özel gagası küçük canlıları süzmesini sağlar.',
    facts:[['Beslenme','Küçük su canlıları'],['Yaşam','Sığ sular']],source:'https://animals.sandiegozoo.org/animals/flamingo',
    rest:['Dinleniyor','Kıyıda sakin biçimde duruyor.'],
    behaviors:{LookAround:['Bakınıyor','Başını ve boynunu hafifçe çevirerek kolonisinin çevresini izliyor.'],Settle:['Rahatlıyor','Boynunu yavaşça toparlayıp daha sakin bir duruşa geçiyor.'],Rest:['Dinleniyor','Kıyıda küçük baş ve boyun hareketleriyle dinleniyor.']},
  },
};

export function describeBehavior(key,detail){
  const profile=ANIMAL_PROFILES[key];
  if(key==='penguin')return [detail.status,profile.behaviors[detail.status]||profile.rest[1]];
  return profile.behaviors[detail.activity]||profile.rest;
}

export function compactBehavior(key,detail){
  if(key==='penguin')return {
    'Bakınıyor':'Çevresini izliyor.','Silkeleniyor':'Gövdesini silkeliyor.','Tüylerini düzeltiyor':'Tüylerine bakım yapıyor.',
    'Uykuya hazırlanıyor':'Çömelip dinleniyor.','Uyuyor':'Kıyıda uyku molasında.','Uyanıyor':'Yavaşça doğruluyor.',
    'Yüzüyor':'Havuzda kısa bir tur.','Suda dinleniyor':'Yüzeyde mola veriyor.',
  }[detail.status]||'Kısa bir mola veriyor.';
  return {rhino:{Look:'Çevresini izliyor.',Ears:'Çevresini dinliyor.',walk:'Ağır adımlarla ilerliyor.'},
    giraffe:{Idle_Source_BlueMesh:'Başını hafifçe çeviriyor.',walk:'Sakin adımlarla ilerliyor.'},
    aviary:{LookAround:'Başını iki yana çeviriyor.',Settle:'Boynunu toparlıyor.',Rest:'Kıyıda dinleniyor.'},
  }[key]?.[detail.activity]||'Kısa bir mola veriyor.';
}
